#!/usr/bin/env python3
import argparse
import sys
import os
import requests
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

    validate_parser = subparsers.add_parser('validate', help='Validate site config')
    validate_parser.add_argument('site', help='Site name')

    args = parser.parse_args()

    if args.command == 'version':
        print('web-to-sheets 1.0.0')
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
        run_site(args.site)


def run_site(site_name):
    logger = Logger()
    config_path = f'sites/{site_name}.yaml'
    try:
        loader = ConfigLoader()
        config = loader.load(config_path)
        scraper = Scraper(config, logger)
        data = scraper.scrape()
        processor = DataProcessor(config, logger)
        processed_data = processor.process(data)
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
