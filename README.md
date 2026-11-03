# Chargeback Tracker CLI

A small, local-first Python CLI for tracking payment disputes and chargebacks.
Built for small businesses, authors, resellers, and anyone who needs to stay on
top of cases, dates, evidence, and outcomes — with no accounts, no API keys,
and nothing leaving your machine.

Made by [Asdale Dynamics, LLC](https://dylanasdale.github.io) — beginner-friendly
AI education, books, and practical tools.

## Who this is for

Dylan Asdale is a registered nurse turned AI author and founder of Asdale
Dynamics, LLC (Indiana, formed October 2026). His book *The Massive AI Manual*
and hub site dylanasdale.github.io explain AI "like a friend would": plain
English, step by step, never condescending.

Asdale Dynamics focuses on beginner-friendly AI education, books and guides,
and practical open-source tools. This CLI is one of those tools — a small
business and author utility for tracking payment disputes and chargebacks.

If you sell on eBay, Amazon, Shopify, or take card payments any other way, you
may eventually deal with a chargeback: a customer disputes a charge, and your
payment processor asks you to respond within a deadline. This tool helps you
keep track of each case, the evidence you've gathered, and the outcome — all in
one plain JSON file on your own computer.

## What it does

- Add a dispute or chargeback case with merchant, processor, transaction ID,
  amount, dates, evidence, and notes
- List your cases, optionally filtered by status (open, under review, evidence
  needed, won, lost, closed)
- See the full details of one case, including how many days are left in your
  response window and whether it's overdue
- Update a case as new evidence comes in or the status changes
- Close a case with an outcome (won or lost)
- Export all cases to CSV so you can open them in a spreadsheet or hand them to
  your bookkeeper
- Everything is stored in a local JSON file (`chargebacks.json` by default).
  Nothing is uploaded, nothing requires an account, and no API keys are needed.

## Install

### Option 1: Run without installing

If you just want to try it out, run the module directly from this folder:

```bash
python3 -m chargeback_tracker.cli --help
```

### Option 2: Install as a command

This makes the `chargeback-tracker` command available everywhere:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
chargeback-tracker --help
```

If `pip install -e .` complains about an "externally managed environment," use:

```bash
pip install -e . --break-system-packages
```

## Usage, step by step

### 1. Add your first case

```bash
chargeback-tracker add \
  --title "Duplicate charge" \
  --merchant "Example Store" \
  --payment-processor Stripe \
  --transaction-id txn_abc123 \
  --amount "42.00" \
  --notes "Customer says they were charged twice."
```

This creates a new case in `chargebacks.json` and prints the case ID. Keep that
ID handy — you'll use it to look the case up later.

### 2. List your cases

```bash
chargeback-tracker list
```

You'll see something like:

```
76571b88  open           42.00 USD  Duplicate charge
```

To see only cases with a particular status:

```bash
chargeback-tracker list --status open
chargeback-tracker list --status under_review
```

### 3. Check the status of one case

The `status` command tells you how many days have passed, how many are left in
the response window, and whether the case is overdue.

```bash
chargeback-tracker status <case-id>
```

You can also check against a specific date (useful when you're catching up on
backlogged cases):

```bash
chargeback-tracker status <case-id> --today 2026-11-10
```

### 4. See full case details

```bash
chargeback-tracker show <case-id>
```

This prints the merchant, amount, status, evidence list, notes, and timestamps.

### 5. Add evidence or change the status

As you gather receipts, screenshots, or emails, add them to the case:

```bash
chargeback-tracker update <case-id> --evidence "receipt.pdf"
chargeback-tracker update <case-id> --status under_review
```

You can also update the merchant, amount, currency, transaction ID, outcome, or
notes in the same command.

### 6. Close the case

When the dispute is resolved, close it with an outcome:

```bash
chargeback-tracker close <case-id> --outcome won
```

Valid outcomes are `won` and `lost`. A closed case is no longer flagged as
overdue.

### 7. Export to CSV

When it's time for bookkeeping, export everything to a spreadsheet-friendly
file:

```bash
chargeback-tracker export --file disputes.csv
```

### 8. Use a different storage file

By default, cases are saved to `chargebacks.json` in your current folder. To
use a different file:

```bash
chargeback-tracker --data-file my_disputes.json list
```

## Storage

Every case is stored as JSON in a single file you control. There is no cloud
backend, no signup, and no personal data collected by Asdale Dynamics. Back up
the JSON file however you like.

## Testing

All tests use Python's built-in `unittest` — nothing extra to install:

```bash
python3 -m unittest discover tests
```

There are 12 tests covering status logic (overdue detection, response windows,
resolved cases, custom reference dates, and status transitions).

## License

MIT. Copyright (c) 2026 Asdale Dynamics, LLC. See LICENSE.
