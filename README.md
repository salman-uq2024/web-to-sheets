# web-to-sheets

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue)](https://www.python.org/)
[![pytest](https://img.shields.io/badge/pytest-testing-green)](https://pytest.org/)
[![gspread](https://img.shields.io/badge/gspread-Google%20Sheets-orange)](https://gspread.readthedocs.io/)

## Overview

`web-to-sheets` is a robust Python CLI tool designed for automating web data extraction and seamless integration with Google Sheets. It empowers users to scrape structured data from websites using configurable CSS selectors, handle authentication securely, validate outputs for quality, and log operations for traceability—all while supporting offline demos for easy experimentation. Whether you're building data pipelines for analysis, monitoring, or reporting, this tool streamlines the process from web to spreadsheet with minimal setup.

Built with a focus on reliability and extensibility, `web-to-sheets` showcases advanced automation techniques, including API interactions with Google Sheets via gspread, ethical web scraping practices, and comprehensive error handling. It's ideal for developers looking to demonstrate skills in CLI design, data processing, and cloud integrations in a real-world project.

## Features

- **Robust Web Scraping**: Extract data using CSS selectors with support for pagination, rate limiting, and domain restrictions to ensure respectful and efficient crawling.
- **Google Sheets Integration**: Automatically export scraped and deduplicated data to Google Sheets, complete with authentication via service accounts for secure, permission-based access.
- **YAML Configuration**: Flexible site-specific configs in YAML format, allowing easy customization of URLs, selectors, output formats, and demo fixtures without code changes.
- **Built-in Validation and Testing**: Includes data validators to enforce quality checks (e.g., minimum rows) and pytest-based unit/integration tests for reliable operation.
- **Demo Scripts and Offline Mode**: Ships with ready-to-run demo scripts and HTML fixtures for quick testing without internet or API keys—perfect for portfolios or onboarding.
- **Logging and Deduplication**: Comprehensive logging to track runs and an in-memory or file-based dedupe store to avoid redundant data entries.

## Quick Start

Getting started is straightforward—even for beginners. Follow these steps from the project root:

1. **Clone and Setup Environment**:
   ```bash
   git clone <repo-url> web-to-sheets
   cd web-to-sheets
   ./scripts/bootstrap.sh  # Creates a virtual environment and installs dependencies in editable mode
   source venv/bin/activate  # Activate the venv (on Windows: venv\Scripts\activate)
   ```

2. **Install Dependencies** (if not using bootstrap):
   ```bash
   pip install -r requirements.txt
   ```

3. **Run Tests**:
   ```bash
   pytest  # Verifies core functionality and demo mode
   ```

4. **List Available Sites**:
   ```bash
   python -m src.cli list-sites  # Or use the 'ws' entrypoint after pip install -e .
   ```

5. **Run a Demo**:
   ```bash
   python -m src.cli run quotes --demo  # Scrapes a local fixture and outputs to CSV
   # Or use the convenience script:
   ./scripts/run_demo.sh
   ```

For a clean reset and fresh run:
```bash
./scripts/fresh_run.sh
```

Detailed installation troubleshooting is in [docs/install.md](docs/install.md). Outputs go to `out/` (CSV/Sheets) and `logs/` for traceability.

## Demo

Experience the tool in action with the built-in `quotes` demo, which uses a local HTML fixture (`docs/fixtures/quotes.html`) to simulate scraping without needing the internet or API credentials.

Run it via:
```bash
./scripts/run_demo.sh
```

This command:
- Loads the `sites/quotes.yaml` config.
- "Scrapes" the fixture file.
- Validates the data (ensuring at least the configured minimum rows).
- Deduplicates results (in-memory for demo).
- Exports to `out/quotes.csv` (Sheets export skipped in demo mode).

Check `logs/` for run details. For production, remove `--demo` to target live sites.

Visualize the workflow with a demo recording (add your own!):

![Demo GIF](demo.gif)

*(Placeholder: Insert a GIF or screenshots here showing the CLI output, CSV results, and Sheets integration. Tools like ScreenFlow or OBS Studio work great for capturing.)*

More demo specifics in [docs/demo.md](docs/demo.md).

## Documentation

- **[Architecture Overview](docs/architecture.md)**: Dive into the modular design, including core components like scraper, processor, and Sheets exporter.
- **[Installation Guide](docs/install.md)**: Step-by-step setup, including Google Sheets auth.
- **[Demo Instructions](docs/demo.md)**: Offline testing and fixture usage.
- **[Operations Guide](docs/ops.md)**: Troubleshooting, config tips, and best practices.

## Skills Demonstrated

This project highlights expertise in:
- Web scraping with ethical considerations (selectors, robots.txt compliance).
- Google APIs integration (gspread for Sheets manipulation).
- CLI development (argparse for user-friendly interfaces).
- Error handling, logging (structlog), and data validation for production-ready code.
- Testing (pytest) and automation scripting for maintainable pipelines.

## Ethical Use

For ethical use only; respect website Terms of Service (TOS), robots.txt files, and API rate limits. This tool is not intended for production scraping without explicit permission from site owners. Always prioritize data privacy and compliance with regulations like GDPR.