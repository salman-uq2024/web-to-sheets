# web-to-sheets

A CLI tool to scrape web data and export results to Google Sheets.

## Installation

1. Clone the repo
2. `pip install -r requirements.txt`
3. Set up service account for Sheets (optional)

## Usage

- `python -m src.cli run <site>` - Run scraper for a configured site
- `python -m src.cli validate <site>` - Validate a site's config file
- `python -m src.cli list-sites` - List available site configs
- `python -m src.cli version` - Print CLI version information

## Config

See `sites/sample.yaml` for config format.
