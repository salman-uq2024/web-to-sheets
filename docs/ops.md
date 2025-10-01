# Operations

## Reset

Use `./scripts/fresh_run.sh` to clear `dedupe.db` and `out/*.csv`, remove old logs,
then run the demo. This ensures a clean state for testing.

## Logs

Run logs are stored in `logs/` with timestamps via the built-in logger. Tail the
newest file to inspect the last execution:

```bash
tail -n 50 $(ls -1t logs/*.log | head -n1)
```

Logs include scrape details, errors, and CSV write confirmations.

## Exit codes

* `0` – Success (data scraped and processed or no new rows in demo mode)
* `1` – General error (e.g., script failures)
* `2` – Insufficient data (fewer rows than `min_rows`)
* `3` – Config validation error
* `4` – Network/Site error

Non-zero codes trigger optional Slack alerts if `SLACK_WEBHOOK_URL` is set in `.env`.
