"""Reads pasted M-Pesa and similar confirmation messages so evidence gets a date, amount and code automatically."""

import re
from dataclasses import dataclass
from datetime import date
from decimal import Decimal, InvalidOperation


@dataclass
class ParsedMessage:
    code: str | None
    amount: Decimal | None
    occurred_on: date | None
    counterparty: str | None
    direction: str | None  # "sent", "received", "paid", "withdrawn" or None

    @property
    def title(self) -> str:
        parts = []
        if self.direction:
            parts.append(self.direction.capitalize())
        if self.amount is not None:
            parts.append(f"KES {self.amount:,.2f}")
        if self.counterparty:
            parts.append(("to " if self.direction in {"sent", "paid"} else "from ") + self.counterparty)
        if self.code:
            parts.append(f"({self.code})")
        return " ".join(parts) or "Message"


CODE = re.compile(r"\b([A-Z0-9]{10})\s+Confirmed", re.IGNORECASE)
AMOUNT = re.compile(r"Ksh\s?([\d,]+(?:\.\d{1,2})?)", re.IGNORECASE)
DATE = re.compile(r"\bon\s+(\d{1,2})/(\d{1,2})/(\d{2,4})")
SENT_TO = re.compile(r"sent to\s+(.+?)(?:\s+\d{9,12}|\s+for account|\s+on\s+\d)", re.IGNORECASE)
PAID_TO = re.compile(r"paid to\s+(.+?)(?:\.|\s+on\s+\d)", re.IGNORECASE)
RECEIVED_FROM = re.compile(r"received\s+Ksh\s?[\d,.]+\s+from\s+(.+?)(?:\s+\d{9,12}|\s+on\s+\d)", re.IGNORECASE)


def parse_message(text: str) -> ParsedMessage:
    text = " ".join(text.split())
    code_match = CODE.search(text)
    amount_match = AMOUNT.search(text)
    amount = None
    if amount_match:
        try:
            amount = Decimal(amount_match.group(1).replace(",", ""))
        except InvalidOperation:
            amount = None

    occurred_on = None
    date_match = DATE.search(text)
    if date_match:
        day, month, year = (int(g) for g in date_match.groups())
        year = year + 2000 if year < 100 else year
        try:
            occurred_on = date(year, month, day)
        except ValueError:
            occurred_on = None

    direction, counterparty = None, None
    for pattern, label in ((SENT_TO, "sent"), (PAID_TO, "paid"), (RECEIVED_FROM, "received")):
        found = pattern.search(text)
        if found:
            direction, counterparty = label, found.group(1).strip().rstrip(".").title()
            break
    if direction is None and re.search(r"withdraw", text, re.IGNORECASE):
        direction = "withdrawn"

    return ParsedMessage(
        code=code_match.group(1).upper() if code_match else None,
        amount=amount,
        occurred_on=occurred_on,
        counterparty=counterparty,
        direction=direction,
    )
