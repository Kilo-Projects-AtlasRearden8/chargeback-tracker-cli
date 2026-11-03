"""Status logic for chargeback cases.

Pure functions over Case dataclasses. Easy to test and easy to reason about.
"""

from __future__ import annotations

from datetime import date, datetime
from typing import Optional

from .models import (
    Case,
    CLOSED,
    EVIDENCE_NEEDED,
    LOST,
    OPEN,
    RESOLVED_STATUSES,
    UNDER_REVIEW,
    VALID_STATUSES,
    WON,
)


def parse_date(value: str) -> date:
    return datetime.strptime(value, "%Y-%m-%d").date()


def days_between(start: date, end: date) -> int:
    return (end - start).days


def compute_status(case: Case, today: Optional[date] = None) -> dict:
    """Return a status summary dict for a case.

    Keys:
        case_id, status, overdue, days_elapsed, days_remaining,
        response_window_days, suggested_status
    """
    today = today or date.today()
    result: dict = {
        "case_id": case.case_id,
        "status": case.status,
        "overdue": False,
        "days_elapsed": None,
        "days_remaining": None,
        "response_window_days": case.response_window_days,
        "suggested_status": case.status,
    }

    if case.status in RESOLVED_STATUSES:
        if case.date_closed:
            result["days_elapsed"] = days_between(
                parse_date(case.date_opened), parse_date(case.date_closed)
            )
        return result

    opened = parse_date(case.date_opened)
    result["days_elapsed"] = days_between(opened, today)
    result["days_remaining"] = case.response_window_days - result["days_elapsed"]

    if result["days_remaining"] <= 0:
        result["overdue"] = True
        if case.status == OPEN:
            result["suggested_status"] = UNDER_REVIEW
    else:
        result["suggested_status"] = case.status

    return result


def is_overdue(case: Case, today: Optional[date] = None) -> bool:
    return compute_status(case, today=today)["overdue"]


def is_valid_transition(from_status: str, to_status: str) -> bool:
    """Whether a case may move from one status to another."""

    if from_status not in VALID_STATUSES or to_status not in VALID_STATUSES:
        return False
    if from_status == to_status:
        return True

    allowed: dict[str, set[str]] = {
        OPEN: {UNDER_REVIEW, EVIDENCE_NEEDED, WON, LOST},
        UNDER_REVIEW: {OPEN, EVIDENCE_NEEDED, WON, LOST},
        EVIDENCE_NEEDED: {UNDER_REVIEW, WON, LOST},
        WON: {CLOSED},
        LOST: {CLOSED},
        CLOSED: {OPEN},  # reopen a closed case if needed
    }

    return to_status in allowed.get(from_status, set())
