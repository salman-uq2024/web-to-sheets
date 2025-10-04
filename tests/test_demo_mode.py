from pathlib import Path

from src.core.database import InMemoryDedupeDB
from src.core.processor import DataProcessor
from src.core.scraper import Scraper


class StubLogger:
    def info(self, *_args, **_kwargs):
        pass

    def error(self, *_args, **_kwargs):
        raise AssertionError("Unexpected error log during test")

    def debug(self, *_args, **_kwargs):
        pass


def test_demo_mode_reads_fixture_and_uses_in_memory_db(tmp_path):
    fixture_path = Path(__file__).resolve().parents[1] / "docs" / "fixtures" / "quotes.html"

    config = {
        "name": "quotes_demo",
        "urls": [fixture_path.as_uri()],
        "selectors": {
            "item": ".quote",
            "text": ".text",
            "author": ".author",
            "link": ".author + a::attr(href)",
        },
        "pagination": {"type": "none"},
        "rate_limit": {"rps": 1, "burst": 1},
        "timeouts": {"connect": 1, "read": 1},
        "headers": {},
        "cookies": {},
        "auth": {"type": "none"},
        "dedupe_keys": ["text"],
        "output": {"sheet_tab": "Sheet1", "csv_dir": str(tmp_path)},
        "min_rows": 1,
        "demo_mode": True,
    }

    logger = StubLogger()
    scraper = Scraper(config, logger)
    data = scraper.scrape(demo_mode=True)

    assert len(data) >= 1

    processor = DataProcessor(config, logger, demo_mode=True)
    assert isinstance(processor.db, InMemoryDedupeDB)

    processed = processor.process(data)
    assert processed == data

    csv_path = tmp_path / f"{config['name']}.csv"
    assert csv_path.exists()
