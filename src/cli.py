#!/usr/bin/env python3
from __future__ import annotations

import argparse
import os
import sys
import uuid
from pathlib import Path
from typing import Sequence

import requests

from . import __version__
from .core.config import ConfigLoader
from .core.logger import Logger
from .core.processor import DataProcessor
from .core.scraper import Scraper
from .core.sheets import SheetsExporter
from .qa.validator import SchemaValidator

EXIT_OK = 0
EXIT_GENERAL = 1
EXIT_INSUFFICIENT_DATA = 2
EXIT_CONFIG = 3
EXIT_RUNTIME = 4

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SITES_DIR = PROJECT_ROOT / "sites"
DEFAULT_DEMO_FIXTURE = PROJECT_ROOT / "docs" / "fixtures" / "quotes.html"


def main(argv: Sequence[str] | None = None) -> int:
    _load_env_file(PROJECT_ROOT / ".env")
    parser = _build_parser()
    args = parser.parse_args(argv)

    if not args.command:
        parser.print_help()
        return EXIT_GENERAL

    if args.command == "version":
        print(f"web-to-sheets {__version__}")
        return EXIT_OK

    if args.command == "list-sites":
        sites = discover_sites(SITES_DIR)
        if not sites:
            print(f"No site configs found in {SITES_DIR}")
            return EXIT_GENERAL
        for site in sites:
            print(site)
        return EXIT_OK

    if args.command == "validate":
        site_name, config_path = resolve_site_config(args.site)
        return validate_site(site_name, config_path)

    if args.command == "validate-all":
        return validate_all_sites(SITES_DIR)

    if args.command == "run":
        site_name, _ = resolve_site_config(args.site)
        return run_site(site_name, demo_mode=args.demo, sites_dir=SITES_DIR)

    parser.print_help()
    return EXIT_GENERAL


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="web-to-sheets CLI")
    subparsers = parser.add_subparsers(dest="command")

    subparsers.add_parser("version", help="Print version")
    subparsers.add_parser("list-sites", help="List available site configs")

    run_parser = subparsers.add_parser("run", help="Run scraper for site")
    run_parser.add_argument("site", help="Site name (with or without .yaml)")
    run_parser.add_argument("--demo", action="store_true", help="Run in offline demo mode")

    validate_parser = subparsers.add_parser("validate", help="Validate one site config")
    validate_parser.add_argument("site", help="Site name (with or without .yaml)")

    subparsers.add_parser("validate-all", help="Validate every site config in sites/")
    return parser


def discover_sites(sites_dir: Path) -> list[str]:
    if not sites_dir.exists():
        return []
    return sorted(path.stem for path in sites_dir.glob("*.yaml"))


def resolve_site_config(site_name: str, sites_dir: Path = SITES_DIR) -> tuple[str, Path]:
    normalized_site = Path(site_name).name.removesuffix(".yaml")
    return normalized_site, sites_dir / f"{normalized_site}.yaml"


def validate_site(site_name: str, config_path: Path) -> int:
    validator = SchemaValidator()
    errors = validator.validate(str(config_path))
    if errors:
        print(f"{site_name}: Invalid")
        for error in errors:
            print(f"- {error}")
        return EXIT_CONFIG
    print(f"{site_name}: Valid")
    return EXIT_OK


def validate_all_sites(sites_dir: Path) -> int:
    sites = discover_sites(sites_dir)
    if not sites:
        print(f"No site configs found in {sites_dir}")
        return EXIT_GENERAL

    invalid_count = 0
    for site in sites:
        config_path = sites_dir / f"{site}.yaml"
        if validate_site(site, config_path) != EXIT_OK:
            invalid_count += 1

    return EXIT_CONFIG if invalid_count else EXIT_OK


def run_site(site_name: str, demo_mode: bool = False, sites_dir: Path = SITES_DIR) -> int:
    logger = Logger()
    _, config_path = resolve_site_config(site_name, sites_dir=sites_dir)
    run_id = uuid.uuid4().hex

    if not config_path.exists():
        logger.error(f"Config file not found: {config_path}")
        _send_failure_alert(logger, site_name=site_name, run_id=run_id, exit_code=EXIT_CONFIG)
        return EXIT_CONFIG

    try:
        loader = ConfigLoader()
        config = loader.load(str(config_path))
        logger.info(f"Configuration loaded: site={site_name}")

        if demo_mode:
            apply_demo_mode(config, logger)
        else:
            start_urls = ", ".join(config.get("urls", []))
            logger.info(f"Live mode active; starting URLs={start_urls}")

        scraper = Scraper(config, logger)
        data = scraper.scrape(demo_mode=demo_mode)
        processor = DataProcessor(config, logger, demo_mode=demo_mode)
        processed_data = processor.process(data)

        if not demo_mode and processed_data:
            exporter = SheetsExporter(config, logger)
            exporter.export(processed_data)

        exit_code = EXIT_OK
    except ValueError as exc:
        message = str(exc)
        logger.error(message)
        exit_code = EXIT_INSUFFICIENT_DATA if "Insufficient data" in message else EXIT_CONFIG
    except requests.RequestException as exc:
        logger.error(f"Network/Site error: {exc}")
        exit_code = EXIT_RUNTIME
    except Exception as exc:  # pragma: no cover - defensive safety net
        logger.error(f"Runtime error: {exc}")
        exit_code = EXIT_RUNTIME

    if exit_code != EXIT_OK:
        _send_failure_alert(logger, site_name=site_name, run_id=run_id, exit_code=exit_code)

    return exit_code


def apply_demo_mode(config: dict, logger: Logger):
    config["demo_mode"] = True
    fixture = Path(config.get("demo_fixture", str(DEFAULT_DEMO_FIXTURE)))
    if not fixture.is_absolute():
        fixture = PROJECT_ROOT / fixture
    fixture = fixture.resolve()

    if not fixture.exists():
        raise ValueError(f"Demo fixture not found: {fixture}")

    config["urls"] = [fixture.as_uri()]
    config["pagination"] = {"type": "none"}
    config["rate_limit"] = {"rps": 1, "burst": 1}
    config.setdefault("output", {})
    config["output"].setdefault("csv_dir", "out")
    logger.info(f"Demo mode active; using fixture {fixture}")


def _send_failure_alert(logger: Logger, site_name: str, run_id: str, exit_code: int):
    webhook_url = os.getenv("SLACK_WEBHOOK_URL")
    if not webhook_url:
        return

    try:
        requests.post(
            webhook_url,
            json={
                "text": f"web-to-sheets run failed: site={site_name}, run_id={run_id}, exit_code={exit_code}"
            },
            timeout=5,
        )
    except requests.RequestException as exc:
        logger.error(f"Failed to send Slack notification: {exc}")


def _load_env_file(path: Path):
    if not path.exists():
        return

    for line in path.read_text(encoding="utf-8").splitlines():
        cleaned = line.strip()
        if not cleaned or cleaned.startswith("#") or "=" not in cleaned:
            continue

        key, value = cleaned.split("=", 1)
        key = key.strip()
        if not key:
            continue

        # Keep shell quoting semantics simple while remaining dependency-free.
        normalized_value = value.strip().strip("'\"")
        os.environ.setdefault(key, normalized_value)


if __name__ == "__main__":
    sys.exit(main())
