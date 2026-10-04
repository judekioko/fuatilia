"""ZIP exports: a case's evidence bundle, and everything held about a user (data subject access request)."""

import io
import json
import zipfile

from django.template.loader import render_to_string
from django.utils import timezone

from .models import Case


def _safe(name: str) -> str:
    keep = "".join(c if c.isalnum() or c in " -_." else "_" for c in name).strip()
    return keep[:80] or "file"


def build_case_bundle(case: Case) -> bytes:
    """Evidence bundle: a printable summary (index.html), a plain-text chronology, letters and the exhibits."""
    buffer = io.BytesIO()
    evidence = list(case.evidence.all())
    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as archive:
        archive.writestr(
            "00-case-summary.html",
            render_to_string("cases/bundle_document.html", {"case": case, "evidence": evidence, "for_zip": True}),
        )
        archive.writestr("01-chronology.txt", render_to_string("cases/bundle_chronology.txt", {"case": case}))
        for index, letter in enumerate(case.letters.order_by("created_at"), start=1):
            archive.writestr(f"letters/{index:02d}-{_safe(letter.subject)}.txt", f"Subject: {letter.subject}\nTo: {letter.recipient}\n\n{letter.body}\n")
        for index, item in enumerate(evidence, start=1):
            label = f"E{index:02d}-{_safe(item.title)}"
            if item.file:
                extension = item.file.name.rsplit(".", 1)[-1]
                with item.file.open("rb") as handle:
                    archive.writestr(f"exhibits/{label}.{extension}", handle.read())
            if item.text:
                archive.writestr(f"exhibits/{label}.txt", item.text)
    return buffer.getvalue()


def build_account_export(user) -> bytes:
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as archive:
        profile = {
            "email": user.email,
            "full_name": user.full_name,
            "phone": user.phone,
            "joined": user.date_joined.isoformat(),
            "consented_at": user.consented_at.isoformat() if user.consented_at else None,
            "exported_at": timezone.now().isoformat(),
        }
        archive.writestr("profile.json", json.dumps(profile, indent=2))
        for case in user.cases.all():
            folder = f"cases/{case.reference}"
            data = {
                "reference": case.reference,
                "title": case.title,
                "category": case.category,
                "against": case.opponent_name,
                "status": case.status,
                "incident_date": case.incident_date.isoformat(),
                "description": case.description,
                "desired_outcome": case.desired_outcome,
                "amount_claimed": str(case.amount_claimed) if case.amount_claimed is not None else None,
                "events": [
                    {"date": e.occurred_on.isoformat(), "kind": e.kind, "title": e.title, "details": e.details}
                    for e in case.events.all()
                ],
                "letters": [
                    {"subject": l.subject, "recipient": l.recipient, "body": l.body, "sent_on": l.sent_on.isoformat() if l.sent_on else None}
                    for l in case.letters.all()
                ],
            }
            archive.writestr(f"{folder}/case.json", json.dumps(data, indent=2))
            archive.writestr(f"{folder}/bundle.zip", build_case_bundle(case))
    return buffer.getvalue()
