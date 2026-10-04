"""Case workflow: opening cases, moving through playbook steps, and keeping the follow-up date right."""

from datetime import date, timedelta

from django.db import IntegrityError, transaction
from django.utils import timezone

from .models import Case, CaseStep, EventKind, Status, StepStatus, TimelineEvent
from .playbooks import get_playbook, playbook_for_category


def today() -> date:
    return timezone.localdate()


@transaction.atomic
def open_case(owner, **fields) -> Case:
    playbook = playbook_for_category(fields["category"])
    case = Case(owner=owner, playbook=playbook.key, **fields)
    # The reference is sequential; retry if two cases are opened at the same moment.
    for attempt in range(3):
        try:
            with transaction.atomic():
                case.save()
            break
        except IntegrityError:
            case.reference = ""
            if attempt == 2:
                raise
    CaseStep.objects.bulk_create(
        CaseStep(case=case, key=step.key, position=index, available_on=today() if index == 0 else None)
        for index, step in enumerate(playbook.steps)
    )
    TimelineEvent.objects.create(
        case=case,
        occurred_on=case.incident_date,
        kind=EventKind.INCIDENT,
        title="Problem happened",
        details=case.description,
        automatic=True,
    )
    TimelineEvent.objects.create(
        case=case, occurred_on=today(), kind=EventKind.NOTE, title="Case opened on Fuatilia", automatic=True
    )
    refresh_follow_up(case)
    return case


def current_step(case: Case) -> CaseStep | None:
    return case.steps.filter(status=StepStatus.PENDING).order_by("position").first()


def refresh_follow_up(case: Case) -> None:
    """The next follow-up is when the next pending step becomes available, unless the user chose a date."""
    if not case.is_active:
        case.next_follow_up = None
    else:
        step = current_step(case)
        case.next_follow_up = step.available_on if step and step.available_on else None
    case.save(update_fields=["next_follow_up", "updated_at"])


@transaction.atomic
def complete_step(case: Case, step: CaseStep, done_on: date | None = None, notes: str = "") -> None:
    playbook = get_playbook(case.playbook)
    definition = playbook.step(step.key)
    done_on = done_on or today()
    step.status = StepStatus.DONE
    step.done_on = done_on
    step.notes = notes[:300]
    step.save()

    TimelineEvent.objects.create(
        case=case,
        occurred_on=done_on,
        kind=EventKind.ESCALATED if definition and definition.escalation else EventKind.CONTACTED,
        title=f"Done: {definition.title if definition else step.key}",
        details=notes,
        automatic=True,
    )
    _schedule_next(case, step, done_on)

    if definition and definition.escalation:
        case.status = Status.ESCALATED
    elif case.status == Status.OPEN:
        case.status = Status.WAITING
    case.save(update_fields=["status", "updated_at"])
    refresh_follow_up(case)


@transaction.atomic
def skip_step(case: Case, step: CaseStep) -> None:
    step.status = StepStatus.SKIPPED
    step.save(update_fields=["status"])
    _schedule_next(case, step, today())
    refresh_follow_up(case)


@transaction.atomic
def reopen_step(case: Case, step: CaseStep) -> None:
    step.status = StepStatus.PENDING
    step.done_on = None
    step.save(update_fields=["status", "done_on"])
    refresh_follow_up(case)


def _schedule_next(case: Case, step: CaseStep, from_date: date) -> None:
    playbook = get_playbook(case.playbook)
    following = case.steps.filter(position__gt=step.position, status=StepStatus.PENDING).order_by("position").first()
    if not following:
        return
    definition = playbook.step(following.key)
    wait = definition.wait_days if definition else 0
    following.available_on = from_date + timedelta(days=wait) if wait else from_date
    following.save(update_fields=["available_on"])


@transaction.atomic
def set_follow_up(case: Case, when: date | None) -> None:
    case.next_follow_up = when
    case.save(update_fields=["next_follow_up", "updated_at"])


@transaction.atomic
def close_case(case: Case, resolved: bool, note: str = "", amount_recovered=None) -> None:
    case.status = Status.RESOLVED if resolved else Status.CLOSED
    case.outcome_note = note
    case.amount_recovered = amount_recovered
    case.closed_at = timezone.now()
    case.next_follow_up = None
    case.save()
    TimelineEvent.objects.create(
        case=case,
        occurred_on=today(),
        kind=EventKind.RESOLVED if resolved else EventKind.CLOSED,
        title="Case resolved" if resolved else "Case closed without resolution",
        details=note,
        automatic=True,
    )


@transaction.atomic
def reopen_case(case: Case) -> None:
    case.status = Status.WAITING if case.steps.filter(status=StepStatus.DONE).exists() else Status.OPEN
    case.closed_at = None
    case.save()
    TimelineEvent.objects.create(case=case, occurred_on=today(), kind=EventKind.NOTE, title="Case reopened", automatic=True)
    refresh_follow_up(case)
