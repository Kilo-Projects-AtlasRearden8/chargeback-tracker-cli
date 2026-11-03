"""Data model for a chargeback/dispute case."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import date, datetime
import uuid

OPEN = "open"
UNDER_REVIEW = "under_review"
EVIDENCE_NEEDED = "evidence_needed"
WON = "won"
LOST = "lost"
CLOSED = "closed"

VALID_STATUSES = {OPEN, UNDER_REVIEW, EVIDENCE_NEEDED, WON, LOST, CLOSED}
RESOLVED_STATUSES = {WON, LOST, CLOSED}

DEFAULT_RESPONSE_WINDOW_DAYS = 30


def generate_case_id() -> str:
    return uuid.uuid4().hex


@dataclass
class Case:
    """A single payment dispute or chargeback case."""

    case_id: str
    title: str
    merchant: str
    payment_processor: str
    transaction_id: str
    amount: str
    currency: str = "USD"
    date_opened: str = field(default_factory=lambda: date.today().isoformat())
    date_closed: str | None = None
    status: str = OPEN
    response_window_days: int = DEFAULT_RESPONSE_WINDOW_DAYS
    evidence: list[str] = field(default_factory=list)
    outcome: str | None = None
    notes: str = ""
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "Case":
        return cls(**data)

    def is_resolved(self) -> bool:
        return self.status in RESOLVED_STATUSES
