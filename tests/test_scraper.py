from urllib.parse import urlparse, parse_qs

from src.core.scraper import Scraper


class StubLogger:
    def info(self, *_args, **_kwargs):
        pass

    def error(self, *_args, **_kwargs):
        pass


def build_base_config():
    return {
        "urls": ["https://example.com/list"],
        "selectors": {"item": ".row", "title": ".title"},
        "pagination": {"type": "query_param", "param": "page", "start": 1, "max_pages": 3},
        "rate_limit": {"rps": 1, "burst": 1},
        "timeouts": {"connect": 1, "read": 1},
        "headers": {},
        "dedupe_keys": ["title"],
        "output": {"sheet_tab": "Sheet1"},
        "min_rows": 1,
        "allowed_domains": ["example.com"],
    }


def test_apply_query_param_preserves_existing_query():
    config = build_base_config()
    scraper = Scraper(config, StubLogger())

    url = scraper._apply_query_param("https://example.com/list?foo=1", "page", 2)

    parsed = urlparse(url)
    query = parse_qs(parsed.query)

    assert query["foo"] == ["1"]
    assert query["page"] == ["2"]
