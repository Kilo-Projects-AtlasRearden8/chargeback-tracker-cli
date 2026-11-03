"""Command-line interface for the chargeback tracker."""

from __future__ import annotations

import argparse
import sys
import uuid
from datetime import date, datetime
from typing import Optional, Sequence

from .export import export_cases
from .models import Case, CLOSED, EVIDENCE_NEEDED, LOST, OPEN, UNDER_REVIEW, WON
from .status import compute_status, is_overdue, is_valid_transition
from .storage import Storage


def _new_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="chargeback-tracker",
        description="Track payment disputes and chargebacks locally (JSON storage, CSV export).",
    )
    parser.add_argument(
        "--data-file",
        default="chargebacks.json",
        help="Local JSON storage file (default: chargebacks.json)",
    )

    sub = parser.add_subparsers(dest="command", required=True)

    add_p = sub.add_parser("add", help="Add a new case")
    add_p.add_argument("--title", required=True)
    add_p.add_argument("--merchant", required=True)
    add_p.add_argument("--payment-processor", required=True)
    add_p.add_argument("--transaction-id", required=True)
    add_p.add_argument("--amount", required=True, help='e.g. "124.50"')
    add_p.add_argument("--currency", default="USD")
    add_p.add_argument("--response-window-days", type=int, default=30)
    add_p.add_argument("--notes", default="")

    list_p = sub.add_parser("list", help="List cases")
    list_p.add_argument("--status", choices=[OPEN, UNDER_REVIEW, EVIDENCE_NEEDED, WON, LOST, CLOSED])

    show_p = sub.add_parser("show", help="Show one case")
    show_p.add_argument("case_id")

    update_p = sub.add_parser("update", help="Update a case")
    update_p.add_argument("case_id")
    update_p.add_argument("--title")
    update_p.add_argument("--merchant")
    update_p.add_argument("--payment-processor")
    update_p.add_argument("--transaction-id")
    update_p.add_argument("--amount")
    update_p.add_argument("--currency")
    update_p.add_argument("--status")
    update_p.add_argument("--response-window-days", type=int)
    update_p.add_argument("--evidence", help="Append an evidence file/note")
    update_p.add_argument("--outcome")
    update_p.add_argument("--notes")

    close_p = sub.add_parser("close", help="Close a resolved case")
    close_p.add_argument("case_id")
    close_p.add_argument("--outcome", choices=[WON, LOST], required=True)
    close_p.add_argument("--notes")

    status_p = sub.add_parser("status", help="Show computed status for a case")
    status_p.add_argument("case_id")
    status_p.add_argument("--today", help="Reference date YYYY-MM-DD (default: today)")

    export_p = sub.add_parser("export", help="Export all cases to CSV")
    export_p.add_argument("--file", required=True, help="Output CSV path")

    delete_p = sub.add_parser("delete", help="Delete a case")
    delete_p.add_argument("case_id")

    return parser


def _cmd_add(args: argparse.Namespace, storage: Storage) -> int:
    case = Case(
        case_id=uuid.uuid4().hex,
        title=args.title,
        merchant=args.merchant,
        payment_processor=args.payment_processor,
        transaction_id=args.transaction_id,
        amount=args.amount,
        currency=args.currency,
        response_window_days=args.response_window_days,
        notes=args.notes,
    )
    storage.add(case, path=args.data_file)
    print(f"Added case {case.case_id}: {case.title}")
    return 0


def _cmd_list(args: argparse.Namespace, storage: Storage) -> int:
    cases = storage.load()
    if args.status:
        cases = [c for c in cases if c.status == args.status]
    if not cases:
        print("No cases found.")
        return 0
    for c in cases:
        flag = "OVERDUE" if is_overdue(c) else ""
        print(f"{c.case_id}  {c.status:14} {c.amount} {c.currency}  {c.title}  {flag}")
    return 0


def _cmd_show(args: argparse.Namespace, storage: Storage) -> int:
    case = storage.find(args.case_id, path=args.data_file)
    if not case:
        print(f"Case not found: {args.case_id}")
        return 1
    summary = compute_status(case)
    print(f"Case ID:     {case.case_id}")
    print(f"Title:       {case.title}")
    print(f"Merchant:    {case.merchant}")
    print(f"Processor:   {case.payment_processor}")
    print(f"Transaction: {case.transaction_id}")
    print(f"Amount:      {case.amount} {case.currency}")
    print(f"Opened:      {case.date_opened}")
    print(f"Status:      {case.status}")
    print(f"Window:      {case.response_window_days} days")
    print(f"Overdue:     {summary['overdue']}")
    if summary["days_remaining"] is not None:
        print(f"Days left:   {summary['days_remaining']}")
    print(f"Outcome:     {case.outcome or '-'}")
    print(f"Evidence:    {', '.join(case.evidence) or '-'}")
    print(f"Notes:       {case.notes or '-'}")
    print(f"Created:     {case.created_at}")
    print(f"Updated:     {case.updated_at}")
    return 0


def _cmd_update(args: argparse.Namespace, storage: Storage) -> int:
    case = storage.find(args.case_id, path=args.data_file)
    if not case:
        print(f"Case not found: {args.case_id}")
        return 1

    changes: dict[str, object] = {}
    for field in (
        "title",
        "merchant",
        "payment_processor",
        "transaction_id",
        "amount",
        "currency",
        "outcome",
        "notes",
    ):
        value = getattr(args, field, None)
        if value is not None:
            changes[field] = value
    if args.status is not None:
        if args.status not in {OPEN, UNDER_REVIEW, EVIDENCE_NEEDED, WON, LOST, CLOSED}:
            print(f"Invalid status: {args.status}")
            return 1
        if not is_valid_transition(case.status, args.status):
            print(f"Invalid transition {case.status} -> {args.status}")
            return 1
        changes["status"] = args.status
    if args.response_window_days is not None:
        changes["response_window_days"] = args.response_window_days
    if args.evidence is not None:
        changes["evidence"] = case.evidence + [args.evidence]

    if not changes:
        print("Nothing to update.")
        return 0

    changes["updated_at"] = datetime.now().isoformat()
    if "status" in changes and changes["status"] in {WON, LOST, CLOSED} and not case.date_closed:
        changes["date_closed"] = date.today().isoformat()

    for key, value in changes.items():
        setattr(case, key, value)

    cases = storage.load()
    cases = [c if c.case_id != case.case_id else case for c in cases]
    storage.save(cases)
    print(f"Updated case {case.case_id}")
    return 0


def _cmd_close(args: argparse.Namespace, storage: Storage) -> int:
    case = storage.find(args.case_id, path=args.data_file)
    if not case:
        print(f"Case not found: {args.case_id}")
        return 1
    if case.is_resolved():
        print(f"Case already resolved: {case.status}")
        return 1

    case.status = CLOSED
    case.outcome = args.outcome
    case.date_closed = date.today().isoformat()
    case.notes = args.notes or case.notes
    case.updated_at = datetime.now().isoformat()

    cases = storage.load()
    cases = [c if c.case_id != case.case_id else case for c in cases]
    storage.save(cases)
    print(f"Closed case {case.case_id} with outcome {args.outcome}")
    return 0


def _cmd_status(args: argparse.Namespace, storage: Storage) -> int:
    case = storage.find(args.case_id, path=args.data_file)
    if not case:
        print(f"Case not found: {args.case_id}")
        return 1
    today = date.today()
    if args.today:
        today = date.fromisoformat(args.today)
    summary = compute_status(case, today=today)
    print(f"Case: {case.case_id} - {case.title}")
    print(f"Status: {summary['status']}")
    print(f"Overdue: {summary['overdue']}")
    if summary["days_elapsed"] is not None:
        print(f"Days elapsed: {summary['days_elapsed']}")
    if summary["days_remaining"] is not None:
        print(f"Days remaining: {summary['days_remaining']}")
    print(f"Suggested: {summary['suggested_status']}")
    return 0


def _cmd_export(args: argparse.Namespace, storage: Storage) -> int:
    cases = storage.load()
    export_cases(cases, args.file)
    print(f"Exported {len(cases)} cases to {args.file}")
    return 0


def _cmd_delete(args: argparse.Namespace, storage: Storage) -> int:
    cases = storage.load()
    kept = [c for c in cases if c.case_id != args.case_id]
    if len(kept) == len(cases):
        print(f"Case not found: {args.case_id}")
        return 1
    storage.save(kept)
    print(f"Deleted case {args.case_id}")
    return 0


_COMMAND_HANDLERS = {
    "add": _cmd_add,
    "list": _cmd_list,
    "show": _cmd_show,
    "update": _cmd_update,
    "close": _cmd_close,
    "status": _cmd_status,
    "export": _cmd_export,
    "delete": _cmd_delete,
}


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = _new_parser()
    args = parser.parse_args(argv)
    storage = Storage(path=args.data_file)
    handler = _COMMAND_HANDLERS[args.command]
    return handler(args, storage)


if __name__ == "__main__":
    sys.exit(main())
