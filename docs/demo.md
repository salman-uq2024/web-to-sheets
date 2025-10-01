# Demo Mode

The project ships with an offline demo that scrapes a local HTML fixture to
avoid hitting real websites during evaluation.

Quick demo
----------

```bash
./scripts/run_demo.sh
```

The script validates the bundled `sites/quotes.yaml` config and runs the CLI in
`--demo` mode. Output is written to `out/quotes.csv` and the latest log file in
`logs/` confirms the run.

Manual demo steps
-----------------

```bash
source venv/bin/activate
python -m src.cli validate quotes
python -m src.cli run quotes --demo
```

Both flows rely exclusively on the fixture at `docs/fixtures/quotes.html`, so
they work fully offline.
