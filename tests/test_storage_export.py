"""Tests for storage and CSV export."""

import csv
import os
import tempfile
import unittest

from chargeback_tracker.models import (
    Case,
    CLOSED,
    LOST,
    OPEN,
    WON,
)
from chargeback_tracker.export import export_cases
from chargeback_tracker.storage import Storage


def make_case(case_id="case-1", status=OPEN, amount="25.00") -> Case:
    return Case(
        case_id=case_id,
        title="Test dispute",
        merchant="Example Store",
        payment_processor="Example Pay",
        transaction_id="txn-123",
        amount=amount,
        status=status,
    )


class StorageTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmpdir = tempfile.mkdtemp()
        self.path = os.path.join(self.tmpdir, "chargebacks.json")

    def test_save_and_load_round_trip(self):
        storage = Storage(path=self.path)
        case = make_case()
        storage.add(case)
        loaded = storage.load()
        self.assertEqual(len(loaded), 1)
        self.assertEqual(loaded[0].case_id, case.case_id)
        self.assertEqual(loaded[0].title, case.title)
        self.assertEqual(loaded[0].status, case.status)

    def test_load_missing_file_returns_empty(self):
        storage = Storage(path=self.path)
        self.assertEqual(storage.load(), [])

    def test_find_returns_case(self):
        storage = Storage(path=self.path)
        storage.add(make_case(case_id="abc"))
        found = storage.find("abc", path=self.path)
        self.assertIsNotNone(found)
        self.assertEqual(found.case_id, "abc")

    def test_find_returns_none_for_missing(self):
        storage = Storage(path=self.path)
        self.assertIsNone(storage.find("nope", path=self.path))

    def test_multiple_cases_persist(self):
        storage = Storage(path=self.path)
        storage.add(make_case(case_id="one", amount="10.00"))
        storage.add(make_case(case_id="two", amount="20.00"))
        loaded = storage.load()
        self.assertEqual(len(loaded), 2)
        amounts = sorted(c.amount for c in loaded)
        self.assertEqual(amounts, ["10.00", "20.00"])


class ExportTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmpdir = tempfile.mkdtemp()
        self.path = os.path.join(self.tmpdir, "disputes.csv")

    def test_export_writes_header_and_rows(self):
        cases = [
            make_case(case_id="one", status=OPEN, amount="10.00"),
            make_case(case_id="two", status=WON, amount="20.00"),
            make_case(case_id="three", status=LOST, amount="5.00"),
        ]
        cases[1].outcome = "Won the dispute"
        export_cases(cases, self.path)
        with open(self.path, newline="", encoding="utf-8") as handle:
            reader = csv.DictReader(handle)
            rows = list(reader)
        self.assertEqual(len(rows), 3)
        self.assertEqual(rows[0]["case_id"], "one")
        self.assertEqual(rows[0]["amount"], "10.00")
        self.assertEqual(rows[1]["status"], WON)
        self.assertEqual(rows[1]["outcome"], "Won the dispute")
        self.assertEqual(rows[2]["status"], LOST)

    def test_export_joins_evidence_with_semicolon(self):
        case = make_case(case_id="one")
        case.evidence = ["receipt.pdf", "screenshot.png"]
        export_cases([case], self.path)
        with open(self.path, newline="", encoding="utf-8") as handle:
            reader = csv.DictReader(handle)
            row = next(reader)
        self.assertEqual(row["evidence"], "receipt.pdf;screenshot.png")


if __name__ == "__main__":
    unittest.main()
