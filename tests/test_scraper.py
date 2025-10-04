from types import SimpleNamespace
from urllib.parse import parse_qs, urlparse

from src.core.scraper import Scraper


class StubLogger:
    def info(self, *_args, **_kwargs):
        pass

    def error(self, *_args, **_kwargs):
        pass

    def debug(self, *_args, **_kwargs):
        pass


def build_base_config():
    return {
        "urls": ["https://example.com/list"],
        "selectors": {"item": ".row", "title": ".title"},
        "pagination": {"type": "query_param", "param": "page", "start": 1, "max_pages": 3},
        "rate_limit": {"rps": 1, "burst": 1},
        "timeouts": {"connect": 1, "read": 1},
        "headers": {"User-Agent": "test-agent"},
        "dedupe_keys": ["title"],
        "output": {"sheet_tab": "Sheet1"},
        "min_rows": 1,
        "allowed_domains": ["example.com"],
        "demo_mode": True,
    }


def test_apply_query_param_preserves_existing_query():
    config = build_base_config()
    scraper = Scraper(config, StubLogger())

    url = scraper._apply_query_param("https://example.com/list?foo=1", "page", 2)

    parsed = urlparse(url)
    query = parse_qs(parsed.query)

    assert query["foo"] == ["1"]
    assert query["page"] == ["2"]


def test_scraper_pagination_query_param(mocker):
    config = build_base_config()
    config["pagination"]["max_pages"] = 2  # Limit to 2 pages for test

    mock_logger = StubLogger()
    scraper = Scraper(config, mock_logger)

    mock_fetch = mocker.patch.object(scraper, "fetch")
    mock_extract = mocker.patch.object(scraper, "extract_items")
    mock_extract.return_value = [{"title": "Item"}]  # 1 item per page

    mock_response1 = SimpleNamespace(text="<html><div class='row'><div class='title'>Page 1</div></div></html>")
    mock_response2 = SimpleNamespace(text="<html><div class='row'><div class='title'>Page 2</div></div></html>")
    mock_fetch.side_effect = [mock_response1, mock_response2]

    # Mock rate_limit to do nothing
    mocker.patch.object(scraper, "rate_limit")

    data = scraper.scrape_url("https://example.com/list")

    assert len(data) == 2  # 2 pages x 1 item
    assert mock_fetch.call_count == 2
    mock_fetch.assert_any_call("https://example.com/list?page=1")
    mock_fetch.assert_any_call("https://example.com/list?page=2")


def test_extract_items_textlist():
    config = build_base_config()
    config["selectors"] = {
        "item": ".quote",
        "text": ".text",
        "tags": ".tag::textlist",
    }

    html = """
    <div class="quote">
        <span class="text">Example quote</span>
        <a class="tag">alpha</a>
        <a class="tag">beta</a>
    </div>
    """

    scraper = Scraper(config, StubLogger())
    from bs4 import BeautifulSoup

    parsed = BeautifulSoup(html, "html.parser")
    items = scraper.extract_items(parsed)

    assert items == [{"text": "Example quote", "tags": "alpha, beta"}]


def test_is_url_disallowed_by_allowed_domains():
    config = build_base_config()
    scraper = Scraper(config, StubLogger())

    assert not scraper._is_url_allowed("https://another.com/page")


def test_is_url_disallowed_by_robots(mocker):
    config = build_base_config()
    config["demo_mode"] = False
    scraper = Scraper(config, StubLogger())

    parser_mock = mocker.Mock()
    parser_mock.can_fetch.return_value = False
    scraper._robot_parsers["example.com"] = parser_mock

    assert not scraper._is_url_allowed("https://example.com/blocked")
    parser_mock.can_fetch.assert_called_once()
