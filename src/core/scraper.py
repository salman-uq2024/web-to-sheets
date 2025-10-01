import time
import random
from pathlib import Path
from types import SimpleNamespace
from urllib.parse import parse_qsl, urlencode, urljoin, urlparse, urlsplit, urlunsplit, unquote

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

    def scrape(self, demo_mode=False):
        self.demo_mode = demo_mode or self.demo_mode
        data = []
        for url in self.config['urls']:
            try:
                if self.allowed_domains and url.startswith(('http://', 'https://')):
                    domain = urlparse(url).netloc
                    if domain not in self.allowed_domains:
                        self.logger.error(f"URL not in allowed domains: {url}")
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
                raise Exception(f"Fixture not found: {e}")
        raise Exception("Max retries exceeded")

    def extract_items(self, soup):
        items = []
        containers = soup.select(self.config['selectors']['item'])
        for container in containers:
            item = {}
            for field, selector in self.config['selectors'].items():
                if field != 'item':
                    clean_selector = selector.split('::')[0]
                    elements = container.select(clean_selector)
                    if elements:
                        if '::attr(' in selector:
                            attr_name = selector.split('::attr(')[1].rstrip(')')
                            item[field] = elements[0].get(attr_name)
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
        return urljoin(current_url, href)

    def rate_limit(self):
        rps = max(self.config.get('rate_limit', {}).get('rps', 1), 1)
        time.sleep(1 / rps)

    def _apply_query_param(self, url, param, value):
        split_url = urlsplit(url)
        query_params = dict(parse_qsl(split_url.query, keep_blank_values=True))
        query_params[param] = str(value)
        new_query = urlencode(query_params, doseq=True)
        return urlunsplit((split_url.scheme, split_url.netloc, split_url.path, new_query, split_url.fragment))
