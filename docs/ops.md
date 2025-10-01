# Operations

## Fresh run

```bash
./scripts/fresh_run.sh
```

The script clears the dedupe database and demo CSV artefacts before running the
offline demo. Use it to showcase a clean scrape.

## Logs

Run logs are stored in `logs/` with timestamps. Tail the newest file to inspect
the last execution:

```bash
tail -n 50 $(ls -1t logs/*.log | head -n1)
```

## Exit codes

* `0` – Success (data scraped and processed or no new rows in demo mode)
* `2` – Scrape produced fewer rows than `min_rows`
* `3` – Config validation error
* `4` – Network/Site error
