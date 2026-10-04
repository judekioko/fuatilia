"""Letter templates. The user is always the sender: Fuatilia assembles their own words and facts into a letter
they review, edit and send themselves. Templates live in templates/letters/<key>.txt."""

from dataclasses import dataclass

from django.template.loader import render_to_string
from django.utils import timezone

from .models import Case


@dataclass(frozen=True)
class LetterTemplate:
    key: str
    name: str
    subject: str
    # Who the letter normally goes to: "opponent" or "regulator".
    audience: str = "opponent"


TEMPLATES: dict[str, LetterTemplate] = {
    t.key: t
    for t in [
        LetterTemplate("complaint", "Formal complaint", "Formal complaint: {title}"),
        LetterTemplate("follow_up", "Follow-up", "Follow-up on my complaint: {title}"),
        LetterTemplate("escalation", "Escalation to a regulator", "Complaint against {opponent}: {title}", "regulator"),
        LetterTemplate("demand", "Final demand", "Final demand: {title}"),
        LetterTemplate("deposit_request", "Request to return deposit", "Request for refund of my deposit"),
        LetterTemplate("deposit_demand", "Final demand for deposit", "Final demand: refund of deposit of KES {amount}"),
        LetterTemplate("telecom_complaint", "Complaint to service provider", "Complaint: {title}"),
        LetterTemplate("reversal_request", "Transaction reversal request", "Request to reverse transaction: {title}"),
    ]
}


def render_letter(case: Case, key: str) -> tuple[str, str]:
    """Returns (subject, body) for a template, filled with the case's facts."""
    template = TEMPLATES[key]
    amount = f"{case.amount_claimed:,.2f}" if case.amount_claimed is not None else ""
    subject = template.subject.format(title=case.title, opponent=case.opponent_name, amount=amount)
    letters_sent = list(case.letters.filter(sent_on__isnull=False).order_by("sent_on"))
    events = list(case.events.exclude(kind="NOTE").order_by("occurred_on", "created_at"))
    body = render_to_string(
        f"letters/{key}.txt",
        {
            "case": case,
            "user": case.owner,
            "today": timezone.localdate(),
            "amount": amount,
            "events": events,
            "evidence": list(case.evidence.all()),
            "letters_sent": letters_sent,
            "first_letter": letters_sent[0] if letters_sent else None,
        },
    ).strip()
    return subject, body


def default_recipient(case: Case, key: str) -> str:
    if TEMPLATES[key].audience == "regulator":
        return ""
    return f"{case.opponent_name}{' <' + case.opponent_contact + '>' if case.opponent_contact else ''}"
