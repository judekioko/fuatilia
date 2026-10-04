from datetime import date, timedelta
from decimal import Decimal

from django import template
from django.utils import timezone

register = template.Library()


@register.filter
def add_days(value: date, days) -> date:
    return value + timedelta(days=int(days))


@register.filter
def kes(value) -> str:
    if value is None or value == "":
        return "—"
    amount = Decimal(value)
    return f"KES {amount:,.0f}" if amount == amount.to_integral() else f"KES {amount:,.2f}"


@register.filter
def days_until(value: date | None) -> int | None:
    if not value:
        return None
    return (value - timezone.localdate()).days


@register.simple_tag
def due_label(value: date | None) -> str:
    """'today', 'tomorrow', 'in 3 days', '2 days overdue'."""
    if not value:
        return ""
    days = (value - timezone.localdate()).days
    if days == 0:
        return "today"
    if days == 1:
        return "tomorrow"
    if days > 1:
        return f"in {days} days"
    return f"{-days} day{'s' if days != -1 else ''} overdue"


STATUS_TONE = {"OPEN": "blue", "WAITING": "amber", "ESCALATED": "purple", "RESOLVED": "green", "CLOSED": "grey"}


@register.filter
def status_tone(status: str) -> str:
    return STATUS_TONE.get(status, "grey")
