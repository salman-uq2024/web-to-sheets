# web-to-sheets CLI Architecture

## Overview

`web-to-sheets` is a Python CLI that loads YAML site configs, scrapes HTML with
Requests + BeautifulSoup, dedupes rows with SQLite, and optionally pushes data
to Google Sheets. A demo mode swaps network calls for a local fixture so the
tool can be showcased without secrets or live traffic.

## Repository layout

```
/
├── .env.example               # Placeholder env vars
├── .gitignore
├── LICENSE
├── README.md
├── docs/
│   ├── architecture.md        # This document
│   ├── demo.md                # Demo walkthrough
│   ├── install.md             # Installation guide
│   ├── ops.md                 # Operational notes
│   └── fixtures/              # Offline HTML fixtures (quotes.html)
├── logs/                      # Log files (gitignored)
├── pyproject.toml             # Packaging metadata (setuptools)
├── requirements.txt           # Compatibility shim (-e . + dev deps)
├── scripts/                   # bootstrap, run_demo, fresh_run helpers
├── sites/
│   └── quotes.yaml            # Public demo config
├── src/
│   ├── cli.py                 # CLI entry point
│   ├── __init__.py            # Package metadata (__version__)
│   ├── core/
│   │   ├── auth.py            # Authentication helpers
│   │   ├── config.py          # YAML loading + defaults
│   │   ├── database.py        # Dedupe stores (SQLite + in-memory)
│   │   ├── logger.py          # File-based logging utility
│   │   ├── processor.py       # Deduping + CSV export
│   │   ├── scraper.py         # HTTP/file scraping + pagination
│   │   └── sheets.py          # Google Sheets integration
│   └── qa/
│       └── validator.py       # Schema validation
└── tests/                     # pytest suite (validator, scraper, demo)
```

## Core components

### Config loading (`src/core/config.py` + `src/qa/validator.py`)

* `ConfigLoader` reads YAML, validates it, and applies defaults for headers,
  auth, rate limits, cookies, etc.
* `SchemaValidator` enforces required fields (`name`, `urls`, `selectors`,
  `pagination`, `dedupe_keys`, `output`, `min_rows`) and checks optional fields
  like `demo_fixture`, `allowed_domains`, and `output.csv_dir`.

### Scraper (`src/core/scraper.py`)

* Uses Requests sessions, configurable timeouts, and simple rate limiting.
* Supports pagination modes (`query_param`, `next_link`, `none`).
* In demo mode, accepts `file://` URLs that map to local fixtures and skips
  network requests altogether.
* Optional `allowed_domains` guard blocks accidental cross-domain requests.

### Processor (`src/core/processor.py`)

* Dedupes rows based on configured keys using `DedupeDB` (SQLite).
* Switches to `InMemoryDedupeDB` in demo/tests to avoid filesystem writes.
* Writes CSV output to a configurable directory (`output.csv_dir`).
* Emits friendly “No new unique rows” logs when duplicates exhaust results.

### Output integrations

* `src/core/sheets.py` appends rows to Google Sheets when `SHEET_ID` and a
  service account are available; otherwise it logs and skips.
* Slack webhook alerts (in `src/cli.py`) fire on non-zero exit codes if
  `SLACK_WEBHOOK_URL` is present.

## CLI flows

* `ws list-sites` – enumerate YAML configs in `sites/` (demo config is tracked,
  others are gitignored).
* `ws validate <site>` – run schema validation and exit with code 3 on error.
* `ws run <site> [--demo]` – scrape & process data. The `--demo` flag rewires
  URLs to the configured fixture, enforces a conservative rate limit, routes
  dedupe to memory, and skips Sheets export.
* `ws version` – print the packaged version (`src.__version__`).

## Data flow

```
config YAML -> ConfigLoader -> Scraper -> DataProcessor -> CSV -> SheetsExporter
                                              \
                                               -> DedupeDB / InMemoryDedupeDB
```

* Demo mode uses `docs/fixtures/quotes.html` as input and writes
  `out/quotes.csv` while keeping dedupe ephemeral.
* Production runs rely on `dedupe.db` to avoid duplicate exports.

## Tooling & automation

* `pyproject.toml` packages the CLI (entry point: `ws`) and declares core deps.
* Tests (pytest) cover validation, pagination helpers, and the demo path.
* GitHub Actions workflow (added alongside the code) runs lint/tests/validation
  on Python 3.11 and 3.12 without network access.

## Extending

1. Add a new `sites/<name>.yaml` config (it will be ignored by git by default).
2. Drop fixture HTML in `docs/fixtures/` if you want an offline demo variant.
3. Update tests to cover new selectors/processors where appropriate.
4. CI will ensure validation + tests keep passing.
