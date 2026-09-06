# Web to Sheets

[![CI](https://github.com/salman-chowdhury/web-to-sheets/actions/workflows/ci.yml/badge.svg)](https://github.com/salman-chowdhury/web-to-sheets/actions/workflows/ci.yml)

A Python CLI for moving permitted web data into CSV and Google Sheets. YAML configuration describes the source, selectors, validation threshold and output columns. An offline fixture makes the extraction workflow reviewable without credentials.

**Start here:** [implementation case study](docs/case-study.md) · [support runbook](docs/ops.md) · [tests](tests)

## Review in five minutes

Requires Python 3.10+.

```bash
git clone https://github.com/salman-chowdhury/web-to-sheets.git
cd web-to-sheets
python -m venv .venv
source .venv/bin/activate
python -m pip install -e '.[dev]'
ws validate-all
ws run quotes --demo
python -m pytest -q
python -m ruff check .
```

Windows activation: `.venv\Scripts\activate`. The demo reads the committed HTML fixture and writes **10 records** to `out/quotes.csv`; it does not call Google Sheets. Inspect the CSV and timestamped files in `logs/`.

## Engineering evidence

| Concern | Implementation / evidence |
| --- | --- |
| Reusable integration | [CLI](src/cli.py), [YAML configuration](sites/quotes.yaml), [Sheets adapter](src/core/sheets.py) |
| Input quality | [Configuration validator](src/qa/validator.py), minimum-row checks and explicit exit codes |
| Duplicate prevention | [Processor](src/core/processor.py) deduplicates within a batch and across successful runs using SQLite |
| Failure recovery | Rows are checkpointed only after CSV writing and confirmed Sheets delivery in live mode; failed delivery exits nonzero and leaves rows retryable |
| Source controls | Allowed domains, robots.txt handling, pagination limits and token-bucket throttling |
| Verification | pytest regression tests, Ruff and GitHub Actions |

## Live integration

Use only sources you are permitted to collect. Set `GOOGLE_SHEETS_ID` and `GOOGLE_SHEETS_CREDENTIALS_PATH` in your environment or local `.env`; grant the service account access to the intended sheet. Configure `output.sheet_tab` in the site YAML, then run `ws run quotes`.

Live runs require a confirmed Sheets delivery before committing deduplication state. Missing configuration or failed delivery returns exit code `4`; the extracted CSV may still exist. See the [runbook](docs/ops.md) before retrying an ambiguous network failure.

## Validation and limits

On 5 September 2026, **29 pytest tests and Ruff passed locally**. Tests mock Google Sheets; this is not a live-account integration certification.

- A lost response after a successful append can still cause duplicates on retry. This is **at-least-once delivery**, not exactly-once processing.
- CSV output is a snapshot of the latest newly extracted batch, not a historical warehouse.
- Parallel workers sharing deduplication state are not coordinated.
- The scraper does not render JavaScript applications; changing page layouts can invalidate selectors.
- Logs are timestamped text, not a distributed tracing system.

## Documentation

[Installation](docs/install.md) · [Demo](docs/demo.md) · [Architecture](docs/architecture.md) · [Operations](docs/ops.md)

MIT licence — see [LICENSE](LICENSE).
