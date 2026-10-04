import uuid
from datetime import date

from django.conf import settings
from django.db import models, transaction
from django.utils import timezone

from .storage import evidence_storage


class Category(models.TextChoices):
    TELECOM = "TELECOM", "Phone, internet or airtime"
    MOBILE_MONEY = "MOBILE_MONEY", "Mobile money (M-Pesa, Airtel Money…)"
    RENT_DEPOSIT = "RENT_DEPOSIT", "Rent deposit not returned"
    BANK = "BANK", "Bank or loan"
    INSURANCE = "INSURANCE", "Insurance claim"
    EMPLOYER = "EMPLOYER", "Employer or salary"
    EDUCATION = "EDUCATION", "School, college or university"
    GOVERNMENT = "GOVERNMENT", "Government office or service"
    MERCHANT = "MERCHANT", "Shop, online seller or delivery"
    TRAVEL = "TRAVEL", "Airline, bus or travel"
    OTHER = "OTHER", "Something else"


class Status(models.TextChoices):
    OPEN = "OPEN", "Open"
    WAITING = "WAITING", "Waiting for a response"
    ESCALATED = "ESCALATED", "Escalated"
    RESOLVED = "RESOLVED", "Resolved"
    CLOSED = "CLOSED", "Closed without resolution"


ACTIVE_STATUSES = [Status.OPEN, Status.WAITING, Status.ESCALATED]


def next_reference() -> str:
    """Human-friendly case reference, e.g. FT-2026-00042. Called inside the save transaction."""
    year = timezone.localdate().year
    prefix = f"FT-{year}-"
    last = (
        Case.objects.select_for_update()
        .filter(reference__startswith=prefix)
        .order_by("-reference")
        .values_list("reference", flat=True)
        .first()
    )
    number = int(last.rsplit("-", 1)[1]) + 1 if last else 1
    return f"{prefix}{number:05d}"


class Case(models.Model):
    public_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="cases")
    reference = models.CharField(max_length=20, unique=True, editable=False)
    title = models.CharField(max_length=140)
    category = models.CharField(max_length=20, choices=Category.choices)
    playbook = models.CharField(max_length=40)
    # The organisation or person the case is against.
    opponent_name = models.CharField("against", max_length=140)
    opponent_contact = models.CharField("their email or phone", max_length=140, blank=True)
    # The opponent's own ticket / reference number, if they gave one.
    opponent_reference = models.CharField("their reference number", max_length=80, blank=True)
    account_reference = models.CharField(
        "your account, phone or policy number with them", max_length=80, blank=True
    )
    incident_date = models.DateField("when it happened")
    description = models.TextField("what happened")
    desired_outcome = models.TextField("what you want them to do")
    amount_claimed = models.DecimalField("amount at stake (KES)", max_digits=12, decimal_places=2, null=True, blank=True)
    amount_recovered = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    status = models.CharField(max_length=12, choices=Status.choices, default=Status.OPEN)
    outcome_note = models.TextField(blank=True)
    # Next date the user should chase; set from playbook steps or by the user.
    next_follow_up = models.DateField(null=True, blank=True)
    last_reminded_on = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    closed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-updated_at"]
        indexes = [models.Index(fields=["owner", "status"])]

    def __str__(self):
        return f"{self.reference} · {self.title}"

    def save(self, *args, **kwargs):
        if not self.reference:
            with transaction.atomic():
                self.reference = next_reference()
                super().save(*args, **kwargs)
            return
        super().save(*args, **kwargs)

    @property
    def is_active(self):
        return self.status in ACTIVE_STATUSES

    @property
    def days_open(self) -> int:
        end = self.closed_at.date() if self.closed_at else timezone.localdate()
        return (end - self.incident_date).days

    @property
    def complaint_deadline(self):
        """Last day to lodge the first complaint, for routes that have a legal limit."""
        from datetime import timedelta

        from .playbooks import get_playbook

        days = get_playbook(self.playbook).complaint_deadline_days
        return self.incident_date + timedelta(days=days) if days else None

    @property
    def complaint_deadline_pending(self) -> bool:
        """True while the case is active and the step that meets the complaint time limit is not done yet."""
        from .playbooks import get_playbook

        playbook = get_playbook(self.playbook)
        if not (self.is_active and playbook.complaint_deadline_days and playbook.complaint_step):
            return False
        return self.steps.filter(key=playbook.complaint_step, status="PENDING").exists()

    @property
    def follow_up_overdue(self) -> bool:
        return bool(self.is_active and self.next_follow_up and self.next_follow_up < timezone.localdate())

    @property
    def follow_up_due_today(self) -> bool:
        return bool(self.is_active and self.next_follow_up == timezone.localdate())


class EvidenceKind(models.TextChoices):
    RECEIPT = "RECEIPT", "Receipt or payment proof"
    MESSAGE = "MESSAGE", "SMS, WhatsApp or M-Pesa message"
    EMAIL = "EMAIL", "Email"
    CONTRACT = "CONTRACT", "Agreement, policy or contract"
    LETTER = "LETTER", "Letter or notice"
    PHOTO = "PHOTO", "Photo"
    SCREENSHOT = "SCREENSHOT", "Screenshot"
    OTHER = "OTHER", "Other document"


def evidence_upload_path(instance, filename):
    extension = filename.rsplit(".", 1)[-1].lower() if "." in filename else "bin"
    return f"evidence/{instance.case.public_id}/{uuid.uuid4().hex}.{extension}"


class Evidence(models.Model):
    case = models.ForeignKey(Case, on_delete=models.CASCADE, related_name="evidence")
    kind = models.CharField(max_length=12, choices=EvidenceKind.choices)
    title = models.CharField(max_length=140)
    file = models.FileField(upload_to=evidence_upload_path, storage=evidence_storage, blank=True)
    original_filename = models.CharField(max_length=200, blank=True)
    content_type = models.CharField(max_length=100, blank=True)
    size = models.PositiveIntegerField(default=0)
    # Pasted text, e.g. an SMS or M-Pesa confirmation message.
    text = models.TextField(blank=True)
    occurred_on = models.DateField("date of this item", null=True, blank=True)
    notes = models.CharField(max_length=300, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["occurred_on", "uploaded_at"]

    def __str__(self):
        return self.title

    @property
    def is_image(self):
        return self.content_type.startswith("image/")

    @property
    def exhibit_number(self) -> int:
        """Position in the evidence bundle (E1, E2…), ordered by date."""
        ids = list(self.case.evidence.values_list("id", flat=True))
        return ids.index(self.id) + 1 if self.id in ids else 0


class EventKind(models.TextChoices):
    INCIDENT = "INCIDENT", "Problem happened"
    CONTACTED = "CONTACTED", "I contacted them"
    RESPONSE = "RESPONSE", "They responded"
    NO_RESPONSE = "NO_RESPONSE", "No response"
    LETTER = "LETTER", "Letter sent"
    ESCALATED = "ESCALATED", "Escalated"
    PAYMENT = "PAYMENT", "Payment or refund"
    NOTE = "NOTE", "Note"
    RESOLVED = "RESOLVED", "Resolved"
    CLOSED = "CLOSED", "Closed"


class TimelineEvent(models.Model):
    case = models.ForeignKey(Case, on_delete=models.CASCADE, related_name="events")
    occurred_on = models.DateField()
    kind = models.CharField(max_length=12, choices=EventKind.choices)
    title = models.CharField(max_length=160)
    details = models.TextField(blank=True)
    evidence = models.ManyToManyField(Evidence, blank=True, related_name="events")
    # Events the app created itself (e.g. "Case opened", "Step completed").
    automatic = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["occurred_on", "created_at"]

    def __str__(self):
        return f"{self.occurred_on}: {self.title}"


class StepStatus(models.TextChoices):
    PENDING = "PENDING", "To do"
    DONE = "DONE", "Done"
    SKIPPED = "SKIPPED", "Skipped"


class CaseStep(models.Model):
    """Progress through one step of the case's playbook."""

    case = models.ForeignKey(Case, on_delete=models.CASCADE, related_name="steps")
    key = models.CharField(max_length=40)
    position = models.PositiveSmallIntegerField()
    status = models.CharField(max_length=8, choices=StepStatus.choices, default=StepStatus.PENDING)
    # The step becomes available on this date (e.g. 14 days after the demand letter).
    available_on = models.DateField(null=True, blank=True)
    done_on = models.DateField(null=True, blank=True)
    notes = models.CharField(max_length=300, blank=True)

    class Meta:
        ordering = ["position"]
        constraints = [models.UniqueConstraint(fields=["case", "key"], name="unique_step_per_case")]

    @property
    def waiting(self) -> bool:
        return bool(self.status == StepStatus.PENDING and self.available_on and self.available_on > date.today())


class Letter(models.Model):
    case = models.ForeignKey(Case, on_delete=models.CASCADE, related_name="letters")
    template = models.CharField(max_length=40)
    subject = models.CharField(max_length=200)
    recipient = models.CharField(max_length=200)
    body = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    sent_on = models.DateField(null=True, blank=True)
    sent_via = models.CharField(max_length=40, blank=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.subject
