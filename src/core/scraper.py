import random
import time
import urllib.robotparser as robotparser
from pathlib import Path
from types import SimpleNamespace
from urllib.parse import parse_qsl, unquote, urlencode, urljoin, urlparse, urlsplit, urlunsplit

import requests
from bs4 import BeautifulSoup

from .auth import Authenticator


class Scraper:
    def __init__(self, config, logger):
        self.config = config
        self.logger = logger
        self.session = requests.Session()
        self.auth = Authenticator(self.session)
        self.auth.authenticate(config.get('auth', {}))
        self.allowed_domains = set(config.get('allowed_domains', []))
        self.demo_mode = config.get('demo_mode', False)
        self._robot_parsers = {}
        rate_limit_cfg = config.get('rate_limit', {}) or {}
        self._rps = max(float(rate_limit_cfg.get('rps', 1)), 0.0)
        default_burst = max(1, int(self._rps)) if self._rps else 1
        self._burst = max(int(rate_limit_cfg.get('burst', default_burst)), 1)
        self._tokens = float(self._burst)
        self._last_refill = time.monotonic()
        headers = config.get('headers', {}) or {}
        self.user_agent = headers.get('User-Agent', 'web-to-sheets/0.1')

    def scrape(self, demo_mode=False):
        self.demo_mode = demo_mode or self.demo_mode
        data = []
        for url in self.config['urls']:
            try:
                if not self._is_url_allowed(url):
                    continue
                items = self.scrape_url(url)
                data.extend(items)
            except Exception as e:
                self.logger.error(f"Failed to scrape {url}: {e}")
        return data

    def scrape_url(self, url):
        items = []
        pagination = self.config.get('pagination', {}) or {}
        pagination_type = pagination.get('type', 'none')
        max_pages = 1 if pagination_type == 'none' else pagination.get('max_pages')

        base_url = url
        current_url = (
            self._apply_query_param(base_url, pagination['param'], pagination.get('start', 1))
            if pagination_type == 'query_param'
            else base_url
        )
        page_number = pagination.get('start', 1) if pagination_type == 'query_param' else None
        page_count = 0

        while max_pages is None or page_count < max_pages:
            if not self._is_url_allowed(current_url):
                self.logger.error(f"Skipping disallowed URL: {current_url}")
                break

            self.rate_limit()
            response = self.fetch(current_url)
            soup = BeautifulSoup(response.text, 'html.parser')
            page_items = self.extract_items(soup)
            items.extend(page_items)
            page_count += 1

            if pagination_type == 'none':
                break

            if max_pages is not None and page_count >= max_pages:
                break

            if pagination_type == 'query_param':
                page_number += 1
                current_url = self._apply_query_param(base_url, pagination['param'], page_number)
            elif pagination_type == 'next_link':
                next_url = self.get_next_url(soup, current_url, pagination)
                if not next_url:
                    break
                current_url = next_url
            else:
                break

        return items

    def fetch(self, url):
        retries = 3
        for attempt in range(retries):
            try:
                parsed = urlsplit(url)
                if parsed.scheme == 'file':
                    path_str = parsed.path
                    if parsed.netloc:
                        path_str = f"//{parsed.netloc}{parsed.path}"
                    file_path = Path(unquote(path_str))
                    if not file_path.exists():
                        raise FileNotFoundError(file_path)

                    with open(file_path, 'r', encoding='utf-8') as handle:
                        text = handle.read()

                    return SimpleNamespace(text=text, raise_for_status=lambda: None)

                if not self._is_url_allowed(url):
                    raise Exception(f"URL disallowed by policy: {url}")

                timeout = (self.config['timeouts']['connect'], self.config['timeouts']['read'])
                response = self.session.get(url, timeout=timeout,
                                            headers=self.config['headers'])
                response.raise_for_status()
                return response
            except requests.exceptions.HTTPError as e:
                if e.response.status_code in (429, 500, 502, 503, 504):
                    wait = (2 ** attempt) + random.uniform(0, 1)
                    time.sleep(wait)
                    continue
                raise
            except FileNotFoundError as e:
                raise Exception(f"Fixture not found: {e}") from e
        raise Exception("Max retries exceeded")

    def extract_items(self, soup):
        items = []
        containers = soup.select(self.config['selectors']['item'])
        for container in containers:
            item = {}
            for field, selector in self.config['selectors'].items():
                if field != 'item':
                    parts = selector.split('::')
                    clean_selector = parts[0]
                    modifier = parts[1] if len(parts) > 1 else None
                    elements = container.select(clean_selector)
                    if elements:
                        if modifier and modifier.startswith('attr('):
                            attr_name = modifier[5:-1]
                            item[field] = elements[0].get(attr_name)
                        elif modifier == 'textlist':
                            texts = [element.get_text(strip=True) for element in elements if element.get_text(strip=True)]
                            item[field] = ', '.join(texts)
                        else:
                            item[field] = elements[0].get_text(strip=True)
            if item:
                items.append(item)
        return items

    def get_next_url(self, soup, current_url, pagination):
        if pagination.get('type') != 'next_link':
            return None
        next_link = soup.select_one(pagination.get('next_selector', ''))
        if not next_link:
            return None
        href = next_link.get('href')
        if not href:
            return None
        next_url = urljoin(current_url, href)
        return next_url

    def rate_limit(self):
        if self._rps <= 0:
            return

        now = time.monotonic()
        elapsed = now - self._last_refill
        self._tokens = min(self._burst, self._tokens + elapsed * self._rps)

        if self._tokens < 1:
            wait_time = (1 - self._tokens) / self._rps
            self.logger.debug(f'Rate limit reached; sleeping for {wait_time:.2f}s')
            time.sleep(wait_time)
            now = time.monotonic()
            elapsed = now - self._last_refill
            self._tokens = min(self._burst, self._tokens + elapsed * self._rps)

        self._tokens = max(0.0, self._tokens - 1)
        self._last_refill = time.monotonic()

    def _apply_query_param(self, url, param, value):
        split_url = urlsplit(url)
        query_params = dict(parse_qsl(split_url.query, keep_blank_values=True))
        query_params[param] = str(value)
        new_query = urlencode(query_params, doseq=True)
        return urlunsplit((split_url.scheme, split_url.netloc, split_url.path, new_query, split_url.fragment))

    def _is_url_allowed(self, url: str) -> bool:
        parsed = urlparse(url)

        if parsed.scheme not in ('http', 'https'):
            return True

        if self.allowed_domains and parsed.netloc not in self.allowed_domains:
            self.logger.error(f"URL not in allowed domains: {url}")
            return False

        if self.demo_mode:
            return True

        parser = self._get_robot_parser(parsed)
        if parser is None:
            return True

        can_fetch = parser.can_fetch(self.user_agent, url)
        if not can_fetch:
            self.logger.error(f"Blocked by robots.txt: {url}")
        return can_fetch

    def _get_robot_parser(self, parsed_url):
        netloc = parsed_url.netloc
        if netloc in self._robot_parsers:
            return self._robot_parsers[netloc]

        robots_url = urlunsplit((parsed_url.scheme, netloc, '/robots.txt', '', ''))
        parser = robotparser.RobotFileParser()
        try:
            timeout = (self.config['timeouts']['connect'], self.config['timeouts']['read'])
            response = self.session.get(robots_url, timeout=timeout, headers=self.config['headers'])
            if response.status_code >= 400:
                self.logger.info(f'robots.txt unavailable for {netloc}; assuming allowed')
                self._robot_parsers[netloc] = None
                return None
            parser.parse(response.text.splitlines())
            self._robot_parsers[netloc] = parser
            return parser
        except requests.RequestException:
            self.logger.info(f'Failed to fetch robots.txt for {netloc}; assuming allowed')
            self._robot_parsers[netloc] = None
            return None
