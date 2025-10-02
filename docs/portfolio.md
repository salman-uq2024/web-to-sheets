# Portfolio Showcase: web-to-sheets

## Project Overview

`web-to-sheets` is a sophisticated Python CLI tool that automates the extraction of structured data from websites and seamlessly integrates it into Google Sheets. Designed for efficiency and reliability, it handles everything from configuration-driven web scraping to data deduplication and API-based exports, all while prioritizing ethical practices and ease of use. This project exemplifies modern software engineering principles in a practical, real-world application—perfect for demonstrating expertise in automation pipelines.

Built as a portfolio piece, it showcases the ability to create maintainable, testable code that solves tangible problems like data collection for analysis, reporting, or monitoring. The tool is production-ready yet accessible, with offline demo capabilities for quick demonstrations without external dependencies.

## Key Features and Technical Highlights

- **Ethical Web Scraping**: Uses Requests and BeautifulSoup for respectful data extraction, incorporating rate limiting, domain restrictions, and pagination support to comply with site policies. Configurable via YAML for site-specific selectors and behaviors.
- **Google Sheets Integration**: Leverages gspread and OAuth2 service accounts for secure, automated appending of scraped data. Handles authentication gracefully, with fallback to CSV exports.
- **Modular Architecture**: Clean separation of concerns—config loading, scraping, processing, and output—in dedicated modules (`src/core/*`). Includes SQLite for deduplication and in-memory alternatives for testing/demos.
- **CLI Design**: Intuitive interface with argparse, supporting commands like `ws run <site> --demo`. Includes validation, listing, and version checks for user-friendly operation.
- **Offline Demo Mode**: Simulates live scraping with local HTML fixtures (e.g., `docs/fixtures/quotes.html`), enabling fully functional showcases without internet or API keys.
- **Robust Testing and Quality**: Comprehensive pytest suite covering core paths, with 100% coverage goals. Includes schema validation and error handling for reliable runs.
- **Logging and Observability**: Structured logs to `logs/` for traceability, with configurable levels and optional Slack notifications on failures.

The data flow—from YAML config to scraped CSV/Sheets—is visualized in [architecture.md](architecture.md) using Mermaid diagrams, highlighting the pipeline's simplicity and extensibility.

## Skills Demonstrated

This project highlights proficiency in several high-demand areas:

- **Python Automation**: End-to-end scripting for data workflows, using libraries like PyYAML, gspread, and sqlite3.
- **Web Scraping with Ethics**: Implementing selectors, handling dynamic content, and built-in safeguards to respect robots.txt and rate limits—crucial for compliant data acquisition.
- **API Integrations**: Secure Google Sheets API usage, including service account setup and error-resilient exports.
- **CLI Development**: Building professional command-line tools with argparse, entry points via setuptools, and user-centric features like help and validation.
- **Software Best Practices**: Modular design patterns, type hints, docstrings, and CI/CD via GitHub Actions. Full test coverage ensures maintainability.
- **Documentation and DX**: Polished Markdown docs (installation, demo, ops, architecture), contributing guidelines, and a ready-to-run demo script for excellent developer experience.

Key achievements include a modular architecture that scales from single-site demos to multi-site pipelines, full test coverage for core functionality, and demo-ready scripts that work offline—making it ideal for interviews or client pitches.

## Use Cases and Impact

`web-to-sheets` is tailored for data automation gigs, such as:
- **Market Research**: Scraping public quotes, news, or product data into Sheets for analysis.
- **Content Monitoring**: Tracking site changes and logging updates without manual effort.
- **Reporting Pipelines**: Automating feeds for dashboards or BI tools.
- **Prototyping**: Quick proofs-of-concept for larger ETL systems.

In a professional setting, it could save hours weekly on manual data entry, with logs and deduplication ensuring data integrity. For scaling, it supports cron jobs, containerization, or orchestration tools like Airflow.

## Getting Started

For a live demo:
1. Follow [install.md](install.md) for setup.
2. Run `./scripts/run_demo.sh` to generate sample CSV from a fixture.
3. Explore configs in `sites/` and extend as needed.

View the full repo structure in [architecture.md](architecture.md) and contribute via [CONTRIBUTING.md](../CONTRIBUTING.md).

This project is open-source (MIT licensed) and ready for collaboration. It's a strong example of turning complex requirements into clean, impactful code—demonstrating readiness for roles in data engineering, automation, or full-stack development.

---

*Last updated: October 2024*