"""Local JSON storage for chargeback cases."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

from .models import Case


class Storage:
    """Read/write cases to a local JSON file."""

    def __init__(self, path: str | Path = "chargebacks.json") -> None:
        self.path = Path(path)

    def load(self) -> list[Case]:
        if not self.path.exists():
            return []
        with self.path.open("r", encoding="utf-8") as handle:
            data = json.load(handle)
        return [Case.from_dict(item) for item in data]

    def save(self, cases: list[Case]) -> None:
        with self.path.open("w", encoding="utf-8") as handle:
            json.dump([case.to_dict() for case in cases], handle, indent=2)
            handle.write("\n")

    def add(self, case: Case, path: Optional[str | Path] = None) -> None:
        target = Path(path) if path else self.path
        cases = Storage(path=target).load()
        cases.append(case)
        Storage(path=target).save(cases)

    def find(self, case_id: str, path: Optional[str | Path] = None) -> Optional[Case]:
        target = Path(path) if path else self.path
        for case in Storage(path=target).load():
            if case.case_id == case_id:
                return case
        return None
