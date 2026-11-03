# Chargeback Tracker CLI

A small, local-first Python CLI for tracking payment disputes and chargebacks.
Built for small businesses, authors, resellers, and anyone who needs to stay on
top of cases, dates, evidence, and outcomes — with no accounts, no API keys,
and nothing leaving your machine.

Made by [Asdale Dynamics, LLC](https://dylanasdale.github.io) — beginner-friendly
AI education, books, and practical tools.

## What it does

- Add dispute/chargeback cases with merchant, processor, transaction, amount,
  dates, evidence, and notes
- List cases (filter by status), show case details, update or close cases
- Status logic: days elapsed, days remaining, and overdue flags based on the
  response window you set per case (default 30 days)
- Export all cases to CSV for bookkeeping or spreadsheets
- All data lives in a local JSON file (`chargebacks.json` by default). Nothing
  is sent anywhere.

## Who this is for

Dylan Asdale is a registered nurse turned AI author and founder of Asdale
Dynamics, LLC (Indiana, formed October 2026). His book *The Massive AI Manual*
and hub site dylanasdale.github.io explain AI "like a friend would": plain
English, step by step, never condescending.

Asdale Dynamics focuses on beginner-friendly AI education, books and guides,
and practical open-source tools. This CLI is one of those tools — a small
business and author utility for payment dispute tracking.

## Install

```bash
git clone <this-repo>
cd chargeback-tracker-cli
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
```

Or just run without installing:

```bash
python3 -m chargeback_tracker.cli --help
```

## Usage

Add a case:

```bash
chargeback-tracker add \
  --title "Duplicate charge" \
  --merchant "Example Store" \
  --payment-processor "Stripe" \
  --transaction-id "txn_abc123" \
  --amount "42.00" \
  --notes "Customer says they were charged twice."
```

List cases:

```bash
chargeback-tracker list
chargeback-tracker list --status open
```

Show one case (includes overdue check and days remaining):

```bash
chargeback-tracker show <case-id>
```

Check computed status with a reference date:

```bash
chargeback-tracker status <case-id> --today 2026-11-10
```

Update a case:

```bash
chargeback-tracker update <case-id> --status under_review --evidence "receipt.pdf"
```

Close a case:

```bash
chargeback-tracker close <case-id> --outcome won
```

Export to CSV:

```bash
chargeback-tracker export --file disputes.csv
```

Use a different storage file:

```bash
chargeback-tracker --data-file my_store.json list
```

## Storage

Cases are stored in JSON, one file you control. Default: `chargebacks.json` in
the current folder. No cloud, no registration, no keys.

## Testing

```bash
python3 -m unittest discover tests
```

## License

MIT. Copyright (c) 2026 Asdale Dynamics, LLC. See LICENSE.
