# Operations Guide

This document covers day-to-day operational aspects of `web-to-sheets`, including resetting the environment, managing logs, handling errors via exit codes, and considerations for scaling the tool in production-like scenarios. It assumes basic familiarity with the CLI and setup (see [install.md](install.md)).

## Resetting the Environment

To start fresh—e.g., for testing or after debugging—use the provided script to clear persistent state:

```bash
./scripts/fresh_run.sh
```

**What it does:**
- Removes `dedupe.db` (SQLite deduplication database) to reset unique row tracking.
- Deletes existing CSV outputs in `out/` to avoid confusion with prior runs.
- Clears old log files in `logs/` (keeps the most recent for reference).
- Activates the virtual environment and runs the demo (`ws run quotes --demo`).

This ensures a clean slate without reinstalling dependencies. For manual resets:
- `rm -f dedupe.db out/*.csv logs/*.log` (be cautious; backs up if needed).
- Then run `ws run <site> [--demo]`.

Use this before demos or when troubleshooting data inconsistencies.

## Logging

Logging is central to observability, capturing config loads, scraping progress, errors, and export confirmations. The tool uses a structured logger (`src/core/logger.py`) that writes to timestamped files in `logs/`.

### Configuration
- Set `LOG_LEVEL` in `.env` (default: `INFO`): Options include `DEBUG` (verbose, for troubleshooting), `INFO` (standard operations), `WARNING` (non-critical issues), `ERROR` (failures only).
- Logs are rotated automatically with filenames like `web-to-sheets-YYYYMMDD-HHMMSS.log`.
- Console output mirrors file logs at the set level for interactive runs.

### Viewing Logs
Tail the latest log for real-time monitoring:

```bash
tail -f $(ls -1t logs/*.log | head -n1)
```

Or view the last 50 lines of the most recent:

```bash
tail -n 50 $(ls -1t logs/*.log | head -n1)
```

**Example Log Entries:**
- `INFO - Config loaded: quotes (validated: True)`
- `INFO - Scraping URL: http://quotes.toscrape.com/page/1 (status: 200)`
- `WARNING - Rate limit applied: Sleeping 1s`
- `ERROR - Selector 'invalid' failed: NoSuchElement`
- `INFO - CSV written: out/quotes.csv (10 rows, 10 unique)`

Logs include timestamps, levels, and context (e.g., site name, URL). For production, integrate with tools like ELK Stack by parsing JSON-formatted logs (enable via logger config).

**Best Practices:**
- Always check logs after runs for anomalies.
- In demo mode, logs confirm "No network calls made" and "In-memory dedupe used".
- Gitignores `logs/` to protect sensitive data (e.g., URLs, auth hints).

## Error Handling

The tool employs robust error handling to fail gracefully, providing actionable feedback via logs and exit codes. Errors are caught at each stage (config, scrape, process, export) and bubbled up without crashing the CLI.

### Exit Codes
Standardized codes indicate the failure point:

- `0`: Success (data processed/exported, or no new rows in dedupe mode).
- `1`: General runtime error (e.g., file I/O issues, invalid arguments).
- `2`: Insufficient data (fewer rows than `min_rows` in config; common in failed scrapes).
- `3`: Configuration validation error (missing required fields in YAML).
- `4`: Network or site-specific error (e.g., 404, timeout, blocked by domain guard).

**Handling in Scripts:**
- Check `$?` after CLI runs: `if [ $? -ne 0 ]; then echo "Failed"; fi`.
- Non-zero codes trigger optional Slack alerts if `SLACK_WEBHOOK_URL` is set in `.env` (sends summary with exit code and log snippet).

### Common Errors and Resolutions
- **Validation Fail (3)**: Run `ws validate <site>` standalone. Fix YAML (e.g., add missing `selectors`).
- **Scrape Fail (4)**: Check logs for HTTP errors. Verify `allowed_domains`, rate limits, or use `--demo`. For auth sites, ensure credentials in config/env.
- **Data Shortfall (2)**: Inspect CSV/logs for partial extracts. Adjust `min_rows` or selectors; test with fixture.
- **Sheets Auth (1/4)**: Confirm `.env` paths/IDs; re-share sheet with service account. Logs detail OAuth errors.
- **General (1)**: Often env-related (e.g., missing deps). Run `pip install -e .[dev]` and check Python version.

All errors log stack traces at `DEBUG` level. For debugging, set `LOG_LEVEL=DEBUG` and re-run.

## Scaling Considerations

While designed for single-site automation, `web-to-sheets` can scale for multi-site or scheduled runs with minimal tweaks.

### Multi-Site Operations
- Run sequentially: Loop over sites in a bash script, e.g.:
  ```bash
  for site in quotes news; do ws run $site; done
  ```
- Parallel: Use `&` for background (monitor with `wait`), but respect rate limits to avoid bans.
- Config: Place multiple YAMLs in `sites/`; use `ws list-sites` to enumerate.

### Scheduling and Automation
- **Cron Jobs**: Schedule daily runs (e.g., `0 2 * * * cd /path/to/project && source venv/bin/activate && ws run quotes`).
  - Add `fresh_run.sh` for periodic resets if dedupe grows large.
  - Redirect logs: `>> logs/cron-$(date +%Y%m%d).log 2>&1`.
- **CI/CD Integration**: GitHub Actions (in `.github/`) already runs tests; extend for scheduled scrapes via workflows.
- **Containerization**: Dockerize for deployment (add Dockerfile with venv setup). Run in Kubernetes for high availability, mounting `sites/` and `logs/` as volumes.

### Performance and Reliability
- **Rate Limiting**: Built-in (configurable in YAML); for heavy use, add proxies or distributed scraping (extend `scraper.py`).
- **Deduplication**: SQLite handles thousands of rows; for millions, migrate to PostgreSQL (swap in `database.py`).
- **Monitoring**: Integrate with Prometheus (expose metrics via logger) or send logs to centralized systems.
- **Resource Usage**: Low footprint (single-threaded); scale vertically (more CPU for parallel) or horizontally (multiple instances per site).
- **Ethical Scaling**: Always throttle requests (e.g., <1/sec per domain). Monitor for site changes via tests.

For large-scale pipelines, consider wrapping in Airflow or Luigi for orchestration.

## Troubleshooting Tips
- No logs generated? Ensure `LOG_LEVEL` is set and permissions allow writes to `logs/`.
- Frequent timeouts? Increase `timeout` in YAML or use VPN/proxies.
- Scaling issues? Profile with `cProfile` on `cli.py` for bottlenecks.

Refer to [architecture.md](architecture.md) for component details and [demo.md](demo.md) for testing ops changes offline.

---

*Last updated: October 2024*