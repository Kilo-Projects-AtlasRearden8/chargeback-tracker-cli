"""Tests for chargeback status logic."""

from datetime import date, timedelta
import unittest

from chargeback_tracker.models import (
    Case,
    CLOSED,
    EVIDENCE_NEEDED,
    LOST,
    OPEN,
    UNDER_REVIEW,
    WON,
)
from chargeback_tracker.status import compute_status, is_overdue, is_valid_transition


def make_case(status=OPEN, days_ago=0, window=30, closed=None) -> Case:
    opened = date.today() - timedelta(days=days_ago)
    return Case(
        case_id="case-1",
        title="Test dispute",
        merchant="Example Store",
        payment_processor="Example Pay",
        transaction_id="txn-123",
        amount="25.00",
        date_opened=opened.isoformat(),
        date_closed=closed.isoformat() if closed else None,
        status=status,
        response_window_days=window,
    )


class ComputeStatusTests(unittest.TestCase):
    def test_open_case_within_window_is_not_overdue(self):
        case = make_case(status=OPEN, days_ago=5, window=30)
        summary = compute_status(case)
        self.assertFalse(summary["overdue"])
        self.assertEqual(summary["days_elapsed"], 5)
        self.assertEqual(summary["days_remaining"], 25)
        self.assertEqual(summary["suggested_status"], OPEN)

    def test_open_case_past_window_is_overdue(self):
        case = make_case(status=OPEN, days_ago=35, window=30)
        summary = compute_status(case)
        self.assertTrue(summary["overdue"])
        self.assertEqual(summary["days_remaining"], -5)
        self.assertEqual(summary["suggested_status"], UNDER_REVIEW)

    def test_exactly_at_window_is_overdue(self):
        case = make_case(status=OPEN, days_ago=30, window=30)
        self.assertTrue(compute_status(case)["overdue"])

    def test_resolved_case_is_never_overdue(self):
        for status in (WON, LOST, CLOSED):
            case = make_case(status=status, days_ago=100, window=30)
            self.assertFalse(compute_status(case)["overdue"])
            self.assertFalse(is_overdue(case))

    def test_custom_today_is_respected(self):
        opened = date(2026, 1, 1)
        case = make_case(status=OPEN, window=30)
        case.date_opened = opened.isoformat()
        summary = compute_status(case, today=date(2026, 1, 20))
        self.assertEqual(summary["days_elapsed"], 19)
        self.assertEqual(summary["days_remaining"], 11)

    def test_days_elapsed_recorded_for_closed_case(self):
        opened = date.today() - timedelta(days=10)
        closed = date.today()
        case = make_case(status=WON, days_ago=0)
        case.date_opened = opened.isoformat()
        case.date_closed = closed.isoformat()
        summary = compute_status(case)
        self.assertEqual(summary["days_elapsed"], 10)


class TransitionTests(unittest.TestCase):
    def test_open_can_move_to_review_evidence_won_lost(self):
        for target in (UNDER_REVIEW, EVIDENCE_NEEDED, WON, LOST):
            self.assertTrue(is_valid_transition(OPEN, target))

    def test_open_cannot_move_directly_to_closed(self):
        self.assertFalse(is_valid_transition(OPEN, CLOSED))

    def test_resolved_can_move_to_closed(self):
        self.assertTrue(is_valid_transition(WON, CLOSED))
        self.assertTrue(is_valid_transition(LOST, CLOSED))

    def test_closed_can_reopen(self):
        self.assertTrue(is_valid_transition(CLOSED, OPEN))

    def test_invalid_statuses_rejected(self):
        self.assertFalse(is_valid_transition(OPEN, "bogus"))
        self.assertFalse(is_valid_transition("bogus", WON))

    def test_same_status_is_valid(self):
        self.assertTrue(is_valid_transition(WON, WON))


if __name__ == "__main__":
    unittest.main()
