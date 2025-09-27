# Web to Sheets Scraper

A CLI tool to scrape web data and export to Google Sheets.

## Installation

1. Clone the repo
2. `pip install -r requirements.txt`
3. Set up service account for Sheets (optional)

## Usage

- `python -m src.cli run <site>` - Run scraper for site
- `python -m src.cli validate <site>` - Validate config
- `python -m src.cli list-sites` - List sites
- `python -m src.cli version` - Version

## Config

See `sites/site.sample.yaml` for config format.