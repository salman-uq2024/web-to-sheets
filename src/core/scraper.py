import requests
from bs4 import BeautifulSoup
import time
import random
from .auth import Authenticator


class Scraper:
    def __init__(self, config, logger):
        self.config = config
        self.logger = logger
        self.session = requests.Session()
        self.auth = Authenticator(self.session)
        self.auth.authenticate(config.get('auth', {}))

    def scrape(self):
        data = []
        for url in self.config['urls']:
            try:
                items = self.scrape_url(url)
                data.extend(items)
            except Exception as e:
                self.logger.error(f"Failed to scrape {url}: {e}")
        return data

    def scrape_url(self, url):
        items = []
        current_url = url
        page = 0
        max_pages = self.config['pagination'].get('max_pages', 1)

        while page < max_pages:
            self.rate_limit()
            response = self.fetch(current_url)
            soup = BeautifulSoup(response.text, 'html.parser')
            page_items = self.extract_items(soup)
            items.extend(page_items)
            page += 1

            next_url = self.get_next_url(soup, current_url, page)
            if not next_url:
                break
            current_url = next_url

        return items

    def fetch(self, url):
        retries = 3
        for attempt in range(retries):
            try:
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

    def get_next_url(self, soup, current_url, page):
        pagination = self.config['pagination']
        if pagination['type'] == 'query_param':
            param = pagination['param']
            # Simple implementation
            next_page = page + 1
            return f"{current_url}?{param}={next_page}"
        elif pagination['type'] == 'next_link':
            next_link = soup.select_one(pagination['next_selector'])
            return next_link['href'] if next_link else None
        return None

    def rate_limit(self):
        rps = self.config['rate_limit']['rps']
        time.sleep(1 / rps)
