# Demo Mode

The project ships with an offline demo that scrapes a local HTML fixture to
avoid hitting real websites during evaluation.

Quick demo
----------

```bash
./scripts/run_demo.sh
```

The script validates the bundled `sites/quotes.yaml` config and runs the CLI in
`--demo` mode. Expected output: `out/quotes.csv` generated with scraped quotes,
no network calls, in-memory dedupe used. Check `logs/` for run details (e.g.,
"CSV written: out/quotes.csv").

Manual demo steps
-----------------

```bash
source venv/bin/activate
ws validate quotes
ws run quotes --demo
```

Both flows rely exclusively on the fixture at `docs/fixtures/quotes.html`, so
they work fully offline. Exit code 0 on success; CSV should contain at least 1 row.
