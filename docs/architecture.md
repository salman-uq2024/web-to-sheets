# web-to-sheets CLI Architecture

## Overview

`web-to-sheets` is a modular Python CLI tool for automating web data extraction and integration with Google Sheets. It loads site configurations from YAML files, scrapes HTML content using Requests and BeautifulSoup, deduplicates rows via SQLite (or in-memory for demos), and optionally exports results to Google Sheets. A demo mode replaces live network calls with local HTML fixtures, enabling offline showcases without secrets or external dependencies.

The design emphasizes reliability, extensibility, and ethical practices: rate limiting, domain guards, and comprehensive logging ensure respectful operation. Built for data automation pipelines, it demonstrates skills in CLI development, web scraping, API integrations, and testing.

## Repository Layout

```
/
├── .env.example               # Template for environment variables (e.g., Sheets credentials)
├── .gitignore
├── LICENSE
├── README.md                  # Project overview and quick start
├── CONTRIBUTING.md            # Guidelines for contributors (see root)
├── docs/                      # Documentation
│   ├── architecture.md        # This document: System design and components
│   ├── demo.md                # Offline demo instructions
│   ├── install.md             # Setup guide
│   ├── ops.md                 # Operational notes (logging, errors)
│   ├── portfolio.md           # Portfolio showcase narrative
│   └── fixtures/              # Local HTML files for demo mode (e.g., quotes.html)
├── logs/                      # Runtime logs (gitignored)
├── pyproject.toml             # Packaging and dependency management (setuptools)
├── requirements.txt           # Compatibility shim for tools expecting it (-e . + dev deps)
├── scripts/                   # Helper scripts (bootstrap.sh, run_demo.sh, fresh_run.sh)
├── sites/                     # YAML configs for sites (quotes.yaml tracked; others gitignored)
├── src/                       # Source code
│   ├── __init__.py            # Package metadata (__version__)
│   ├── cli.py                 # CLI entrypoint (argparse-based commands)
│   └── core/                  # Core modules
│       ├── auth.py            # Authentication utilities (e.g., basic auth, service accounts)
│       ├── config.py          # YAML loading and default application
│       ├── database.py        # Deduplication storage (SQLite or in-memory)
│       ├── logger.py          # Structured logging to files
│       ├── processor.py       # Data processing, deduplication, and CSV export
│       ├── scraper.py         # HTTP/file scraping with pagination and rate limiting
│       └── sheets.py          # Google Sheets API integration (gspread)
│   └── qa/
│       └── validator.py       # Schema validation for configs and data
└── tests/                     # Pytest suite (scraper, validator, demo mode)
```

Dependencies are declared in [`pyproject.toml`](pyproject.toml) (e.g., requests, beautifulsoup4, gspread). Install via `pip install -e .[dev]` for development.

## Core Components

### Configuration Loading (`src/core/config.py` + `src/qa/validator.py`)

- `ConfigLoader`: Parses YAML files from `sites/`, applies defaults for headers, auth, rate limits, cookies, and pagination.
- `SchemaValidator`: Enforces structure with required fields (`name`, `urls`, `selectors`, `pagination`, `dedupe_keys`, `output`, `min_rows`) and optionals like `demo_fixture`, `allowed_domains`, `output.csv_dir`. Exits with code 3 on validation errors.

Configs support demo overrides (e.g., `demo_fixture: docs/fixtures/quotes.html`) for offline testing.

### Web Scraper (`src/core/scraper.py`)

- Leverages Requests sessions with configurable timeouts, retries, and user-agent rotation.
- Handles pagination via modes: `query_param` (e.g., `?page=2`), `next_link` (follows `<a rel="next">`), or `none`.
- In demo mode, `file://` URLs load local fixtures, bypassing network calls.
- Enforces allowed domains and consults `robots.txt` (unless in demo mode) before fetching, backed by a token-bucket rate limiter (`rps` + `burst`).
- Extracts data using BeautifulSoup CSS selectors, yielding rows as dictionaries and supporting multi-value selectors (e.g., `::textlist`).

Ethical note: Always check `robots.txt` and site TOS before live use.

### Data Processor (`src/core/processor.py`)

- `DedupeDB`: Uses SQLite (`dedupe.db`) for persistent deduplication based on `dedupe_keys`; switches to `InMemoryDedupeDB` in demo/tests.
- Processes scraped rows: Validates against `min_rows`, removes duplicates, and exports to CSV in `output.csv_dir` (default: `out/`).
- Logs summaries like "No new unique rows added" to avoid unnecessary exports.

### Output Integrations

- **Google Sheets (`src/core/sheets.py`)**: Appends new rows to a specified sheet using `gspread.service_account`. Requires `GOOGLE_SHEETS_CREDENTIALS_PATH` and `GOOGLE_SHEETS_ID` in `.env` (legacy aliases still supported). Skips in demo mode with a log message.
- **CSV Export**: Always generates files for traceability.
- **Notifications (`src/cli.py`)**: Optional Slack webhooks on non-zero exit codes via `SLACK_WEBHOOK_URL`.

### Authentication (`src/core/auth.py`)

- Supports basic auth (username/password from env or config).
- Handles Google service account JSON for Sheets (no user intervention needed post-setup).

## CLI Flows

The CLI (`ws`) provides intuitive commands:

- `ws list-sites`: Lists YAML configs in `sites/` (only `quotes` is version-controlled).
- `ws validate <site>`: Validates a config; exits 3 on failure.
- `ws run <site> [--demo]`: Full pipeline: load → scrape → process → export. `--demo` enables offline mode.
- `ws version`: Displays package version from `src/__init__.py`.

Example: `ws run quotes --demo` generates `out/quotes.csv` from the fixture.

## Data Flow Diagram

The pipeline follows a linear flow with branching for storage and outputs. Below is a Mermaid diagram illustrating the process:

```mermaid
graph TD
    A[CLI Command: ws run <site>] --> B[Load YAML Config<br/>sites/<site>.yaml]
    B --> C[Validate Schema<br/>src/qa/validator.py]
    C --> D[Scrape Data<br/>src/core/scraper.py<br/>(Live URLs or Fixture)]
    D --> E[Process & Deduplicate<br/>src/core/processor.py<br/>SQLite or In-Memory DB]
    E --> F[Export CSV<br/>out/<site>.csv]
    E --> G{Sheets Enabled?}
    G -->|Yes| H[Append to Google Sheets<br/>src/core/sheets.py<br/>gspread service account]
    G -->|No/Demo| I[Log Skip]
    F --> J[Log Summary & Exit]
    H --> J
    I --> J
    style D fill:#e1f5fe
    style E fill:#f3e5f5
    style H fill:#e8f5e8
```

- **Key Paths**:
  - Demo: Config → Fixture Scrape → In-Memory Dedupe → CSV (Sheets skipped).
  - Production: Config → Live Scrape → SQLite Dedupe → CSV + Sheets.
- Logs are emitted throughout via `src/core/logger.py` to `logs/`.

## Tooling and Automation

- **Packaging**: `pyproject.toml` enables `pip install -e .` for the `ws` entrypoint.
- **Testing**: Pytest covers validation, scraping helpers, and demo flows (`tests/test_*.py`). Run with `pytest` (no network required).
- **Linting**: Ruff for style checks (integrated in dev deps).
- **CI/CD**: GitHub Actions (in `.github/`) run tests/lint on Python 3.10–3.12.
- **Scripts**: `bootstrap.sh` for setup, `run_demo.sh` for quick runs, `fresh_run.sh` for resets.

## Extending the Project

1. Add a new YAML config in `sites/<new-site>.yaml` (auto-gitignored for secrets).
2. Place fixture HTML in `docs/fixtures/` and reference via `demo_fixture`.
3. Update selectors/processors in `scraper.py` or `processor.py` if needed.
4. Add tests in `tests/` for new logic.
5. Run `ws validate <new-site>` and `pytest` to verify.
6. For production scaling, see [ops.md](ops.md).

This architecture ensures modularity: Swap scrapers, add outputs (e.g., JSON), or integrate new auth without breaking the core flow.

---

*Last updated: October 2024*
