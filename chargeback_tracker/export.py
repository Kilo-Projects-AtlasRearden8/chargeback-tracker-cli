"""CSV export for chargeback cases."""

from __future__ import annotations

import csv
from pathlib import Path

from .models import Case


FIELDNAMES = [
    "case_id",
    "title",
    "merchant",
    "payment_processor",
    "transaction_id",
    "amount",
    "currency",
    "date_opened",
    "date_closed",
    "status",
    "response_window_days",
    "evidence",
    "outcome",
    "notes",
    "created_at",
    "updated_at",
]


def export_cases(cases: list[Case], file_path: str | Path) -> None:
    with Path(file_path).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDNAMES)
        writer.writeheader()
        for case in cases:
            row = case.to_dict()
            row["evidence"] = ";".join(row["evidence"])
            writer.writerow(row)
