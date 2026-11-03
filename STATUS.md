# STATUS.md

## What was built

A local-first Python CLI for small businesses to track payment disputes and
chargebacks. Cases track title, merchant, payment processor, transaction ID,
amount, currency, dates, status, response window, evidence, outcome, and notes.

Features:
- `add`, `list`, `show`, `update`, `close`, `status`, `export`, `delete`
- Local JSON storage (`chargebacks.json` by default, configurable with
  `--data-file`); nothing leaves your machine, no accounts or API keys
- CSV export for bookkeeping/spreadsheets
- Status logic: days elapsed, days remaining, overdue flag, and suggested next
  status based on a per-case response window (default 30 days); resolved cases
  are never flagged overdue
- Status transition validation (e.g. open -> closed is not allowed directly)
- Tests for status logic plus storage and CSV export (19 tests, stdlib unittest
  only)

Made by Asdale Dynamics, LLC. MIT licensed.

## How to run

```bash
# from the project folder
python3 -m chargeback_tracker.cli --help

# add a case
python3 -m chargeback_tracker.cli --data-file cb.json add \
  --title "Duplicate charge" --merchant "Example Store" \
  --payment-processor Stripe --transaction-id txn_abc123 \
  --amount "42.00" --notes "Charged twice."

# list, check status, export
python3 -m chargeback_tracker.cli --data-file cb.json list
python3 -m chargeback_tracker.cli --data-file cb.json status <case-id> --today 2026-11-10
python3 -m chargeback_tracker.cli --data-file cb.json export --file disputes.csv

# run tests
python3 -m unittest discover tests

# install (optional)
pip install -e .
chargeback-tracker --help
```

## Verification results

- `python3 -m py_compile chargeback_tracker/*.py tests/*.py` — OK
- `python3 -m unittest discover tests` — 19 tests, OK (12 status logic + 7
  storage/export)
- `pip install -e .` + `chargeback-tracker --help` — entry point works
- End-to-end smoke test — add, list, status (overdue detection with custom
  reference date), close, export CSV all verified manually

## Known gaps

- CLI is flag-driven only (no interactive prompts)
- Amount stored as a string; no currency conversion or arithmetic
- No duplicate-transaction detection
- Single-file JSON storage; no concurrent-write locking
- No config file beyond `--data-file`/environment
