#!/usr/bin/env python3
import argparse
import sys
import os
from pathlib import Path

import requests
from . import __version__
from .core.config import ConfigLoader
from .core.scraper import Scraper
from .core.processor import DataProcessor
from .core.sheets import SheetsExporter
from .core.logger import Logger
from .qa.validator import SchemaValidator


def main():
    parser = argparse.ArgumentParser(description='web-to-sheets CLI')
    subparsers = parser.add_subparsers(dest='command')

    subparsers.add_parser('version', help='Print version')

    subparsers.add_parser('list-sites', help='List available sites')

    run_parser = subparsers.add_parser('run', help='Run scraper for site')
    run_parser.add_argument('site', help='Site name')
    run_parser.add_argument('--demo', action='store_true', help='Run in offline demo mode')

    validate_parser = subparsers.add_parser('validate', help='Validate site config')
    validate_parser.add_argument('site', help='Site name')

    args = parser.parse_args()

    if args.command == 'version':
        print(f'web-to-sheets {__version__}')
        sys.exit(0)

    elif args.command == 'list-sites':
        sites = [f.replace('.yaml', '') for f in os.listdir('sites') if f.endswith('.yaml')]
        for site in sites:
            print(site)

    elif args.command == 'validate':
        validator = SchemaValidator()
        errors = validator.validate(f'sites/{args.site}.yaml')
        if errors:
            for error in errors:
                print(error)
            sys.exit(3)  # Config error
        print('Valid')

    elif args.command == 'run':
        run_site(args.site, demo_mode=args.demo)


def run_site(site_name, demo_mode=False):
    logger = Logger()
    config_path = f'sites/{site_name}.yaml'
    try:
        loader = ConfigLoader()
        config = loader.load(config_path)
        if demo_mode:
            config['demo_mode'] = True
            fixture = config.get('demo_fixture', 'docs/fixtures/quotes.html')
            fixture_path = Path(fixture)
            if not fixture_path.is_absolute():
                fixture_path = Path.cwd() / fixture
            if not fixture_path.exists():
                raise ValueError(f'Demo fixture not found: {fixture_path}')
            config['urls'] = [fixture_path.as_uri()]
            config['pagination'] = {'type': 'none'}
            config['rate_limit'] = {'rps': 1, 'burst': 1}
            config.setdefault('allowed_domains', ['quotes.toscrape.com'])
            config.setdefault('output', {})
            config['output'].setdefault('csv_dir', 'out')
        scraper = Scraper(config, logger)
        data = scraper.scrape(demo_mode=demo_mode)
        processor = DataProcessor(config, logger,
                                  demo_mode=demo_mode)
        processed_data = processor.process(data)
        if not demo_mode:
            exporter = SheetsExporter(config, logger)
            if processed_data:
                exporter.export(processed_data)
        exit_code = 0
    except ValueError as e:
        logger.error(str(e))
        if 'Insufficient data' in str(e):
            exit_code = 2
        else:
            exit_code = 3
    except Exception as e:
        logger.error(f"Network/Site error: {e}")
        exit_code = 4

    # Alert hook
    if exit_code != 0 and os.getenv('SLACK_WEBHOOK_URL'):
        run_id = 'some_id'  # Generate unique run ID
        requests.post(os.getenv('SLACK_WEBHOOK_URL'), json={
            'text': f"web-to-sheets run failed: site={site_name}, run_id={run_id}, exit_code={exit_code}"
        })

    sys.exit(exit_code)


if __name__ == '__main__':
    main()
