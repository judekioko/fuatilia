from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import connection
from django.db.models import Count, Q, Sum
from django.http import FileResponse, Http404, HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.http import require_POST

from . import services
from .exports import build_case_bundle
from .forms import (
    CaseForm,
    CategoryForm,
    CloseCaseForm,
    EventForm,
    EvidenceForm,
    FollowUpForm,
    LetterForm,
    LetterSentForm,
    NewLetterForm,
    StepDoneForm,
)
from .letters import TEMPLATES, default_recipient, render_letter
from .models import ACTIVE_STATUSES, Case, Category, EventKind, Letter, Status, StepStatus, TimelineEvent
from .playbooks import get_playbook, playbook_for_category
from .uploads import INLINE_TYPES


def home(request):
    if request.user.is_authenticated:
        return redirect("dashboard")
    return render(request, "home.html", {"categories": Category.choices})


def privacy(request):
    return render(request, "privacy.html")


def health(request):
    with connection.cursor() as cursor:
        cursor.execute("SELECT 1")
    return JsonResponse({"status": "ok"})


def owned_case(request, reference: str) -> Case:
    # Scoped to the signed-in owner: other people's cases are indistinguishable from missing ones.
    return get_object_or_404(Case, owner=request.user, reference=reference)


@login_required
def dashboard(request):
    cases = request.user.cases.all()
    active = list(cases.filter(status__in=ACTIVE_STATUSES).order_by("next_follow_up", "-updated_at"))
    today = timezone.localdate()
    due = [c for c in active if c.next_follow_up and c.next_follow_up <= today]
    upcoming = [c for c in active if c not in due]
    closed = cases.exclude(status__in=ACTIVE_STATUSES).order_by("-closed_at")[:10]
    totals = cases.aggregate(
        at_stake=Sum("amount_claimed", filter=Q(status__in=ACTIVE_STATUSES)),
        recovered=Sum("amount_recovered"),
        resolved=Count("id", filter=Q(status=Status.RESOLVED)),
    )
    for case in active:
        step = services.current_step(case)
        definition = get_playbook(case.playbook).step(step.key) if step else None
        case.next_step_title = definition.title if definition else "Waiting for an outcome"
    return render(
        request,
        "cases/dashboard.html",
        {"due": due, "upcoming": upcoming, "closed": closed, "totals": totals, "active_count": len(active)},
    )


@login_required
def case_new(request):
    category = request.GET.get("category") or request.POST.get("category")
    if category not in Category.values:
        return render(request, "cases/new_category.html", {"form": CategoryForm(), "categories": Category.choices})

    form = CaseForm(request.POST or None, category=category, initial={"incident_date": timezone.localdate()})
    if request.method == "POST" and form.is_valid():
        case = services.open_case(request.user, category=category, **form.cleaned_data)
        messages.success(request, f"Case {case.reference} opened. Add your evidence next.")
        return redirect("case_detail", reference=case.reference)
    playbook = playbook_for_category(category)
    return render(
        request,
        "cases/new_details.html",
        {"form": form, "category": category, "category_label": Category(category).label, "playbook": playbook},
    )


@login_required
def case_detail(request, reference):
    case = owned_case(request, reference)
    playbook = get_playbook(case.playbook)
    steps = []
    current = services.current_step(case)
    for step in case.steps.all():
        definition = playbook.step(step.key)
        if definition:
            steps.append({"record": step, "definition": definition, "is_current": current and step.pk == current.pk})
    evidence = list(case.evidence.all())
    checklist = playbook.evidence_checklist
    return render(
        request,
        "cases/detail.html",
        {
            "case": case,
            "playbook": playbook,
            "steps": steps,
            "current": current,
            "events": case.events.prefetch_related("evidence"),
            "evidence": evidence,
            "letters": case.letters.all(),
            "checklist": checklist,
            "step_form": StepDoneForm(),
            "follow_up_form": FollowUpForm(initial={"next_follow_up": case.next_follow_up}),
            "close_form": CloseCaseForm(),
            "letter_choices": TEMPLATES,
            "tab": request.GET.get("tab", "steps"),
        },
    )


@login_required
def case_edit(request, reference):
    case = owned_case(request, reference)
    form = CaseForm(request.POST or None, instance=case)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Case details updated.")
        return redirect("case_detail", reference=case.reference)
    return render(request, "cases/edit.html", {"form": form, "case": case})


@login_required
@require_POST
def step_done(request, reference, step_id):
    case = owned_case(request, reference)
    step = get_object_or_404(case.steps, pk=step_id)
    form = StepDoneForm(request.POST)
    if form.is_valid():
        services.complete_step(case, step, form.cleaned_data["done_on"], form.cleaned_data["notes"])
        messages.success(request, "Step marked as done. We'll remind you when the next one is due.")
    else:
        messages.error(request, "Choose a valid date.")
    return redirect("case_detail", reference=case.reference)


@login_required
@require_POST
def step_skip(request, reference, step_id):
    case = owned_case(request, reference)
    step = get_object_or_404(case.steps, pk=step_id, status=StepStatus.PENDING)
    services.skip_step(case, step)
    return redirect("case_detail", reference=case.reference)


@login_required
@require_POST
def step_reopen(request, reference, step_id):
    case = owned_case(request, reference)
    step = get_object_or_404(case.steps, pk=step_id)
    services.reopen_step(case, step)
    return redirect("case_detail", reference=case.reference)


@login_required
def evidence_add(request, reference):
    case = owned_case(request, reference)
    form = EvidenceForm(request.POST or None, request.FILES or None)
    if request.method == "POST" and form.is_valid():
        item = form.save_for(case)
        if request.POST.get("add_to_timeline") and item.occurred_on:
            event = TimelineEvent.objects.create(
                case=case, occurred_on=item.occurred_on, kind=EventKind.NOTE, title=item.title
            )
            event.evidence.add(item)
        messages.success(request, f"Added “{item.title}”.")
        if request.POST.get("another"):
            return redirect("evidence_add", reference=case.reference)
        return redirect(f"{reverse('case_detail', args=[case.reference])}?tab=evidence")
    return render(request, "cases/evidence_form.html", {"form": form, "case": case})


@login_required
def evidence_file(request, reference, evidence_id):
    case = owned_case(request, reference)
    item = get_object_or_404(case.evidence, pk=evidence_id)
    if not item.file:
        raise Http404
    inline = item.content_type in INLINE_TYPES
    response = FileResponse(
        item.file.open("rb"),
        content_type=item.content_type or "application/octet-stream",
        as_attachment=not inline,
        filename=item.original_filename or item.file.name.rsplit("/", 1)[-1],
    )
    response["X-Content-Type-Options"] = "nosniff"
    response["Cache-Control"] = "private, no-store"
    return response


@login_required
@require_POST
def evidence_delete(request, reference, evidence_id):
    case = owned_case(request, reference)
    item = get_object_or_404(case.evidence, pk=evidence_id)
    if item.file:
        item.file.delete(save=False)
    item.delete()
    messages.success(request, "Evidence removed.")
    return redirect(f"{reverse('case_detail', args=[case.reference])}?tab=evidence")


@login_required
def event_add(request, reference):
    case = owned_case(request, reference)
    form = EventForm(request.POST or None, case=case)
    if request.method == "POST" and form.is_valid():
        event = form.save(commit=False)
        event.case = case
        event.save()
        form.save_m2m()
        if event.kind == EventKind.RESPONSE and case.status == Status.OPEN:
            case.status = Status.WAITING
            case.save(update_fields=["status", "updated_at"])
        messages.success(request, "Added to the timeline.")
        return redirect(f"{reverse('case_detail', args=[case.reference])}?tab=timeline")
    return render(request, "cases/event_form.html", {"form": form, "case": case})


@login_required
@require_POST
def event_delete(request, reference, event_id):
    case = owned_case(request, reference)
    get_object_or_404(case.events, pk=event_id, automatic=False).delete()
    return redirect(f"{reverse('case_detail', args=[case.reference])}?tab=timeline")


@login_required
@require_POST
def letter_new(request, reference):
    case = owned_case(request, reference)
    form = NewLetterForm(request.POST)
    if form.is_valid():
        key = form.cleaned_data["template"]
        subject, body = render_letter(case, key)
        letter = Letter.objects.create(
            case=case, template=key, subject=subject, body=body, recipient=default_recipient(case, key)
        )
        return redirect("letter_edit", reference=case.reference, letter_id=letter.pk)
    return redirect(f"{reverse('case_detail', args=[case.reference])}?tab=letters")


@login_required
def letter_edit(request, reference, letter_id):
    case = owned_case(request, reference)
    letter = get_object_or_404(case.letters, pk=letter_id)
    form = LetterForm(request.POST or None, instance=letter)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Letter saved.")
        return redirect("letter_edit", reference=case.reference, letter_id=letter.pk)
    return render(
        request,
        "cases/letter_edit.html",
        {"form": form, "case": case, "letter": letter, "sent_form": LetterSentForm()},
    )


@login_required
def letter_print(request, reference, letter_id):
    case = owned_case(request, reference)
    letter = get_object_or_404(case.letters, pk=letter_id)
    return render(request, "cases/letter_print.html", {"case": case, "letter": letter})


@login_required
@require_POST
def letter_sent(request, reference, letter_id):
    case = owned_case(request, reference)
    letter = get_object_or_404(case.letters, pk=letter_id)
    form = LetterSentForm(request.POST)
    if form.is_valid():
        letter.sent_on = form.cleaned_data["sent_on"]
        letter.sent_via = form.cleaned_data["sent_via"]
        letter.save(update_fields=["sent_on", "sent_via"])
        TimelineEvent.objects.create(
            case=case,
            occurred_on=letter.sent_on,
            kind=EventKind.LETTER,
            title=f"Sent: {letter.subject}",
            details=f"Sent by {letter.sent_via} to {letter.recipient}",
            automatic=True,
        )
        if case.status == Status.OPEN:
            case.status = Status.WAITING
            case.save(update_fields=["status", "updated_at"])
        messages.success(request, "Recorded as sent and added to the timeline.")
    return redirect("case_detail", reference=case.reference)


@login_required
@require_POST
def letter_delete(request, reference, letter_id):
    case = owned_case(request, reference)
    get_object_or_404(case.letters, pk=letter_id).delete()
    return redirect(f"{reverse('case_detail', args=[case.reference])}?tab=letters")


@login_required
@require_POST
def follow_up_set(request, reference):
    case = owned_case(request, reference)
    form = FollowUpForm(request.POST)
    if form.is_valid():
        services.set_follow_up(case, form.cleaned_data["next_follow_up"])
        messages.success(request, "Reminder updated.")
    return redirect("case_detail", reference=case.reference)


@login_required
@require_POST
def case_close(request, reference):
    case = owned_case(request, reference)
    form = CloseCaseForm(request.POST)
    if form.is_valid():
        services.close_case(
            case,
            resolved=form.cleaned_data["outcome"] == "resolved",
            note=form.cleaned_data["note"],
            amount_recovered=form.cleaned_data["amount_recovered"],
        )
        messages.success(request, "Case closed. Well done for seeing it through.")
    return redirect("case_detail", reference=case.reference)


@login_required
@require_POST
def case_reopen(request, reference):
    case = owned_case(request, reference)
    services.reopen_case(case)
    return redirect("case_detail", reference=case.reference)


@login_required
@require_POST
def case_delete(request, reference):
    case = owned_case(request, reference)
    for item in case.evidence.exclude(file=""):
        item.file.delete(save=False)
    case.delete()
    messages.success(request, "Case and its documents deleted.")
    return redirect("dashboard")


@login_required
def bundle_view(request, reference):
    case = owned_case(request, reference)
    return render(request, "cases/bundle_document.html", {"case": case, "evidence": list(case.evidence.all())})


@login_required
def bundle_zip(request, reference):
    case = owned_case(request, reference)
    response = HttpResponse(build_case_bundle(case), content_type="application/zip")
    response["Content-Disposition"] = f'attachment; filename="{case.reference}-evidence-bundle.zip"'
    return response
