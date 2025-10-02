# Contributing to web-to-sheets

Thank you for your interest in contributing to `web-to-sheets`! This project welcomes contributions that improve its functionality, documentation, or usability. Whether it's fixing bugs, adding features, enhancing tests, or refining docs, your help is appreciated.

To get started, follow the guidelines below. All contributors must adhere to the project's [code of conduct](CODE_OF_CONDUCT.md) (if added) and respect ethical scraping practices.

## Development Setup

Before contributing, set up a development environment:

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/yourusername/web-to-sheets.git  # Replace with actual repo
   cd web-to-sheets
   ```

2. **Create and Activate Virtual Environment**:
   Use the bootstrap script for ease:
   ```bash
   ./scripts/bootstrap.sh
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
   
   This installs the project in editable mode (`-e .[dev]`) with all dependencies, including dev tools like pytest and ruff.

3. **Install Additional Tools** (if needed):
   - Ensure `ruff` is available: `pip install ruff` (included in dev deps).
   - For Google Sheets testing, configure `.env` as per [install.md](docs/install.md).

4. **Verify Setup**:
   ```bash
   ws --help  # Check CLI works
   pytest     # Run tests
   ```

Branch off `main` for your changes: `git checkout -b feature/your-feature`.

## Running Tests

The project uses [pytest](https://docs.pytest.org/) for unit and integration tests, covering validation, scraping, processing, and demo mode. Tests are offline-friendly (no network required).

### Running the Test Suite
```bash
pytest  # All tests
pytest tests/test_scraper.py  # Specific file
pytest -v -s  # Verbose output
pytest --cov=src  # Coverage report (requires pytest-cov; install if needed)
```

- Tests live in `tests/` and use fixtures for mocking (e.g., HTML responses).
- Aim for 100% coverage on new code; run `pytest --cov-fail-under=100` to enforce.
- For Sheets integration tests, mock gspread or use a test sheet (see `tests/conftest.py` if added).

If tests fail, check logs in `logs/` or run with `DEBUG` logging.

## Linting and Code Style

We use [Ruff](https://docs.astral.sh/ruff/) for linting and formatting, enforcing PEP 8 style with some custom rules. No separate black/isort needed—Ruff handles it.

### Running Linting
```bash
ruff check .  # Lint all files
ruff check --fix .  # Auto-fix issues
ruff format .  # Format code (if configured)
```

- Configured via `pyproject.toml` (or add `.ruff.toml` for project-specific rules).
- Pre-commit hook (optional): Install with `pre-commit install` after `pip install pre-commit`, then it runs ruff on git commits.
- Focus areas: Imports (no unused), type hints (where practical), docstrings (Google style).

Run `ruff check --output-format=github` before PRs for CI-friendly output.

## Code Style Guidelines

- **Python Version**: Target 3.10+; use type hints liberally (`from typing import ...`).
- **Structure**: Keep modules focused (e.g., `scraper.py` for HTTP only). Use classes for complex logic (e.g., `ConfigLoader`).
- **Comments/Docstrings**: Use Google-style docstrings for functions/classes. Inline comments for non-obvious logic.
- **Error Handling**: Raise specific exceptions (e.g., `ValueError` for validation); log before raising.
- **Ethical Code**: Include rate limiting in scrapers; document any external deps (e.g., site TOS).
- **Commits**: Use conventional commits (e.g., `feat: add new selector support`, `fix: resolve dedupe bug`).

Review [architecture.md](docs/architecture.md) for design patterns.

## Reporting Issues

Found a bug or have a feature request? Open an issue on GitHub:

1. Search existing issues to avoid duplicates.
2. Provide details:
   - Steps to reproduce (e.g., `ws run quotes --demo`).
   - Expected vs. actual behavior.
   - Environment (Python version, OS, logs snippet).
   - Screenshots or CSV samples if relevant.
3. For bugs: Include exit code and log excerpts (redact secrets).

Label issues as `bug`, `enhancement`, or `question`. The maintainer will triage promptly.

Security issues? Email privately (add contact) instead of opening a public issue.

## Submitting Pull Requests

1. **Fork and Branch**: Fork the repo, create a feature branch.
2. **Develop**: Make changes, commit often with clear messages.
3. **Test Locally**:
   ```bash
   pytest
   ruff check .
   ws validate quotes  # Manual check
   ```
4. **Push and PR**:
   - Push to your fork: `git push origin feature/your-feature`.
   - Open a PR against `main`.
   - Describe changes, reference issues (e.g., "Fixes #42").
   - Include test updates and docs if impacted.

PRs must pass CI (lint + tests). Expect review for style, tests, and docs. Merge via squash or rebase.

## Extending the Project

To add support for new sites or features:

1. **New Site Config**:
   - Create `sites/<new-site>.yaml` with `urls`, `selectors`, `dedupe_keys`, etc. (gitignored by default for secrets).
   - Add `demo_fixture` in `docs/fixtures/` for offline testing.
   - Validate: `ws validate <new-site>`.
   - Test: `ws run <new-site> --demo`.

2. **New Features**:
   - E.g., Add JSON export: Extend `processor.py`, update CLI in `cli.py`.
   - Add pagination mode: Modify `scraper.py`.
   - For Sheets: Enhance `sheets.py` (e.g., batch appends).

3. **Testing Extensions**:
   - Add tests in `tests/` (e.g., `test_new_site.py`).
   - Mock external calls (use `pytest-mock`).

4. **Documentation**:
   - Update README.md or docs/ for user-facing changes.
   - Add examples in demo.md if relevant.

5. **CI Updates**: If adding deps, update `pyproject.toml` and test matrix in `.github/workflows/`.

Contributions adding new integrations (e.g., other APIs) are especially welcome—propose in an issue first.

## Code of Conduct

By participating, you agree to our [code of conduct](CODE_OF_CONDUCT.md). Harassment-free environment for all.

Questions? Open an issue or discuss in PR comments. Happy contributing!

---

*Last updated: October 2024*