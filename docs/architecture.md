# web-to-sheets CLI Architecture

## Overview
A Python-based CLI tool for scraping web data and exporting to Google Sheets. Uses minimal libraries: requests, beautifulsoup4, yaml, gspread, oauth2client, sqlite3 (built-in). Optional selenium for JavaScript-heavy sites.

## File Structure
```
/
├── docs/
│   └── architecture.md          # This document
├── logs/                        # Log files
├── scripts/                     # Utility scripts (e.g., setup)
├── sites/                       # YAML config files per site
│   └── sample.yaml              # Example config
├── src/
│   ├── cli.py                   # Thin CLI entry point
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py            # YAML loading/validation
│   │   ├── scraper.py           # Web scraping logic
│   │   ├── processor.py         # Data processing/dedupe
│   │   ├── sheets.py            # Google Sheets integration
│   │   ├── database.py          # SQLite for dedupe/idempotency
│   │   ├── logger.py            # Logging utilities
│   │   └── auth.py              # Authentication handling
│   └── qa/
│       └── validator.py         # YAML schema validation
├── requirements.txt             # Python dependencies
└── README.md                    # User docs
```

## Key Modules and Classes

### src/core/config.py
- `ConfigLoader`: Loads and validates YAML against schema.
- Validates required fields, types, and cross-references (e.g., dedupe_keys exist in selectors).

### src/core/scraper.py
- `Scraper`: Handles HTTP requests with rate limiting, retries (exponential backoff + jitter for 429/5xx), timeouts.
- Supports pagination (query_param, next_link).
- Extracts data using CSS selectors configured per site.

### src/core/processor.py
- `DataProcessor`: Dedupes data using configured keys and SQLite tracking.
- Validates data integrity.
- Prepares data for CSV and Sheets export.

### src/core/sheets.py
- `SheetsExporter`: Authenticates via service account (if SHEET_ID set), updates sheets idempotently.
- Appends new rows when Google Sheets credentials are available; otherwise logs and skips export.

### src/core/database.py
- `DedupeDB`: SQLite (or JSONL) wrapper for persistent dedupe tracking across runs.
- Ensures idempotent runs.

### src/core/logger.py
- Structured logging to files in logs/, with levels (INFO, ERROR).

### src/core/auth.py
- `Authenticator`: Applies HTTP basic auth via environment credentials and provides a placeholder for form-based logins.

### src/qa/validator.py
- `SchemaValidator`: Validates required fields, URLs (http(s)), pagination rules, dedupe_keys references.

## Additional Features
- **CSV Output**: Always write CSV per run.
- **Sheets Integration**: Conditional on SHEET_ID and service account.
- **Persistent Dedupe**: Across runs via SQLite.
- **Exit Codes**: 0 (success), 2 (below min_rows), 3 (config error), 4 (network/site error).
- **Alert Hook**: Slack webhook on non-zero exit if SLACK_WEBHOOK_URL set.

## CLI Subcommands Execution Flow

### `python -m src.cli run <site>`
1. Load config from sites/<site>.yaml
2. Validate config via validator.py
3. Initialize DB connection for dedupe
4. For each URL:
   - Authenticate if needed
   - Scrape with rate limiting/retries
   - Extract data
5. Process data: dedupe against DB, validate
6. Export new data to Google Sheets
7. Log success/failures
8. Close DB

### `python -m src.cli validate <site>`
1. Load sites/<site>.yaml
2. Run SchemaValidator
3. Print validation errors or "Valid"

### `python -m src.cli list-sites`
1. List YAML files in sites/

### `python -m src.cli version`
1. Print version string from `src/cli.py`

## Component Interactions and Data Flow
- **Config** -> **CLI** -> **Validator** (validate) or **Scraper**
- **Scraper** -> Raw HTML/JSON -> **Processor** -> Cleaned data -> **DedupeDB** -> **SheetsExporter**
- **Logger** integrated throughout for errors, progress.
- **Auth** called by Scraper for secured sites.

Features:
- **Idempotent**: DB prevents re-scraping duplicates.
- **Dedupe**: Based on configured keys.
- **Rate Limiting**: Via time.sleep or library.
- **Retries**: Up to 3 attempts with backoff.
- **Logging**: File-based, structured.
- **Multiple URLs**: Iterates over every URL declared in the site config.

Aligns with YAML schema: Enforces required fields, optional defaults.
