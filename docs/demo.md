# Demo Mode

The `web-to-sheets` project includes a fully offline demo mode to showcase its functionality without requiring internet access, API credentials, or live web scraping. This mode uses a local HTML fixture to simulate data extraction, making it ideal for presentations, testing, or portfolio demonstrations.

Demo mode activates via the `--demo` flag in the CLI, which:
- Rewires configured URLs to point to local fixture files (e.g., `file://docs/fixtures/quotes.html`).
- Skips network requests and uses in-memory deduplication to avoid filesystem dependencies.
- Disables Google Sheets export to prevent authentication issues.
- Enforces conservative rate limiting and validation checks.

The bundled demo focuses on scraping quotes from a simulated "Quotes to Scrape" site, extracting text, authors, and tags.

## Running the Demo with `scripts/run_demo.sh`

The project provides a convenience script for quick execution. This script assumes the virtual environment is set up (see [installation guide](install.md)).

```bash
./scripts/run_demo.sh
```

**What the script does:**
1. Checks for the existence of the `venv` directory; exits with an error if missing (run `./scripts/bootstrap.sh` first).
2. Activates the virtual environment (`source venv/bin/activate`).
3. Runs the CLI command: `ws run quotes --demo`.
   - Loads the configuration from `sites/quotes.yaml`.
   - Validates the config using the built-in schema checker.
   - "Scrapes" the local fixture, processes the data (deduplication, CSV export).
   - Logs the entire process to `logs/` with timestamps.

The script uses `set -euo pipefail` for robust error handling, ensuring it fails fast on issues.

**Expected Output:**
- Console logs: Messages like "Config loaded: quotes", "Scraping URL: file://docs/fixtures/quotes.html", "Found 10 quotes", "CSV written: out/quotes.csv", "Demo mode: Skipping Sheets export".
- Generated file: `out/quotes.csv` with columns for `quote`, `author`, and `tags` (comma-separated).
- Log file: A new entry in `logs/` (e.g., `logs/web-to-sheets-YYYYMMDD-HHMMSS.log`) detailing the run, including any validation results.
- Exit code: 0 on success (data processed) or non-zero if validation fails (e.g., fewer than `min_rows`).

Example CSV snippet (from fixture):
```
quote,author,tags
“The world as we have created it is a process of our thinking. It cannot be changed without changing our thinking.”,Albert Einstein,change,deep-thoughts,thinking,world
“It is our choices, Harry, that show what we truly are, far more than our abilities.”,J.K. Rowling,abilities,choices
...
```

If no new unique rows are found (unlikely in demo), it logs "No new unique rows" and exits successfully.

## Manual Demo Steps

For more control or debugging, run the commands manually after activating the environment:

```bash
source venv/bin/activate  # Activate venv if needed
ws validate quotes        # Validate config (exit code 3 on error)
ws run quotes --demo      # Run the demo (CLI entrypoint)
```

- `ws validate quotes`: Checks `sites/quotes.yaml` against the schema (required fields like `urls`, `selectors`, `dedupe_keys`).
- `ws run quotes --demo`: Executes the full pipeline in demo mode.

Both steps rely on the fixture and work offline. Use `ws list-sites` to see available configs (only `quotes` is tracked in git).

## Fixture Explanation: `docs/fixtures/quotes.html`

The demo uses a static HTML file (`docs/fixtures/quotes.html`) mimicking the structure of [quotes.toscrape.com](http://quotes.toscrape.com/), a popular scraping tutorial site. This fixture contains:

- 10 sample quotes in `<div class="quote">` elements.
- Each quote includes:
  - Text in `<span class="text">`.
  - Author in `<small class="author">`.
  - Tags in `<div class="tags">` with links (e.g., `<a class="tag">change</a>`).
- Pagination simulation: A "Next" link, but demo config limits to one page.
- Full HTML structure with Bootstrap CSS classes for realism.

The fixture is derived from public sample data and does not contain real-time or copyrighted content. In production configs, you can add your own fixtures for other sites by placing HTML files in `docs/fixtures/` and referencing them via `demo_fixture` in YAML.

To inspect the fixture:
```bash
cat docs/fixtures/quotes.html  # View raw HTML
# Or open in a browser for visual rendering
```

## Expected Outputs and Validation

- **CSV Export**: `out/quotes.csv` with at least 10 rows (one per quote). Columns match the `output` config in `sites/quotes.yaml` (e.g., `quote`, `author`, `tags` joined by commas).
- **Logs**: Detailed entries in `logs/`, including:
  - Config loading and validation success.
  - Scraping summary (e.g., "Extracted 10 rows from 1 page").
  - Deduplication (e.g., "All 10 rows unique").
  - Export confirmation.
- **No Sheets Update**: In demo mode, logs "Demo mode active: Skipping Sheets export".
- **Validation**: Ensures `min_rows: 5` is met; fails with exit code 2 if not.

If the CSV has fewer rows than expected, check logs for selector mismatches or config issues.

## Troubleshooting

- **Script fails on venv**: Run `./scripts/bootstrap.sh` to set up the environment.
- **CLI not found**: Ensure `pip install -e .[dev]` was executed in the activated venv.
- **No output CSV**: Verify `out/` directory permissions; check logs for errors like "Insufficient data".
- **Fixture missing**: The file is included in the repo; re-clone if deleted.

For production runs (live scraping), omit `--demo` and ensure `.env` is configured. See [architecture](architecture.md) for the full data flow and [operations](ops.md) for scaling tips.

---

*Last updated: October 2024*