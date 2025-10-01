# web-to-sheets

`web-to-sheets` is a Python CLI that loads site configs, scrapes pages with
CSS selectors, dedupes results, and optionally exports to Google Sheets. The
repository ships with an offline-friendly demo so anyone can try it without
secrets.

## Quickstart

```bash
./scripts/bootstrap.sh   # create venv and install in editable mode
source venv/bin/activate
pytest                   # run unit + demo tests
python -m src.cli list-sites
python -m src.cli run quotes --demo
```

See `docs/install.md` for more detail.

## Demo Mode

The `quotes` site config is wired to a local HTML fixture. Run it offline via:

```bash
./scripts/run_demo.sh
```

Output lands in `out/quotes.csv`, and `logs/` records the run. Internally the
demo uses an in-memory dedupe store, so it never writes `dedupe.db`.

## Fresh Run

Reset demo artefacts and re-run in one step:

```bash
./scripts/fresh_run.sh
```

## CLI Reference

```bash
ws list-sites
ws validate <site>
ws run <site> [--demo]
ws version
```

The `ws` entry point is provided by `pip install -e .`; using `python -m
src.cli` also works.

## Configs

- `sites/quotes.yaml` – public demo config (online target with optional
  pagination).
- Add private configs as new YAML files under `sites/`. They are ignored by
  default via `.gitignore`.

Configs must declare URLs, selectors, pagination, dedupe keys, output, and
`min_rows`. Optional extras include rate limits, allowed domains, and a
`demo_fixture` for offline use. See `docs/architecture.md` for module-level
details.

## Optional Sheets Export

Sheets support activates when both `SHEET_ID` and `service_account.json` are
present. Copy `.env.example` to `.env`, fill in the placeholders, and provide a
Google service account file (kept out of source control). Runs without these
settings skip export gracefully.

## Troubleshooting

- **“Demo fixture not found”** – ensure `docs/fixtures/quotes.html` exists and
  you are running from the repo root.
- **Exit code 2 (“Insufficient data”)** – loosen `min_rows` or verify selectors
  in the site config.
- **No new rows** – remove `dedupe.db` (or use `fresh_run.sh`) to reset state.

Operational tips live in `docs/ops.md`; demo-specific notes are in
`docs/demo.md`.
