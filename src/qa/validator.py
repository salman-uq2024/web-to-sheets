import yaml
import os


class SchemaValidator:
    def __init__(self):
        self.errors = []

    def validate(self, config_path):
        if not os.path.exists(config_path):
            self.errors.append(f"Config file not found: {config_path}")
            return self.errors

        try:
            with open(config_path, 'r') as f:
                config = yaml.safe_load(f)
        except yaml.YAMLError as e:
            self.errors.append(f"YAML parse error: {e}")
            return self.errors

        # Required fields
        required = ['name', 'urls', 'selectors', 'pagination', 'dedupe_keys', 'output', 'min_rows']
        for req in required:
            if req not in config:
                self.errors.append(f"Missing required field: {req}")

        if 'urls' in config and (not isinstance(config['urls'], list) or len(config['urls']) < 1):
            self.errors.append("urls must be a non-empty list")

        if 'selectors' in config:
            if 'item' not in config['selectors']:
                self.errors.append("selectors must include 'item'")
            selector_fields = [k for k in config['selectors'] if k != 'item']
            if len(selector_fields) < 1:
                self.errors.append("selectors must have at least one field besides 'item'")
            if 'dedupe_keys' in config and not all(k in config['selectors']
                                                   for k in config['dedupe_keys']):
                self.errors.append("dedupe_keys must reference existing selector fields")

        if 'pagination' in config:
            if config['pagination'].get('type') not in ['query_param', 'next_link', 'none']:
                self.errors.append("pagination.type must be query_param, next_link, or none")
            if config['pagination']['type'] == 'query_param':
                if ('param' not in config['pagination'] or
                        'start' not in config['pagination'] or
                        'max_pages' not in config['pagination']):
                    self.errors.append("pagination query_param requires param, start, max_pages")
            elif config['pagination']['type'] == 'next_link':
                if 'next_selector' not in config['pagination']:
                    self.errors.append("pagination next_link requires next_selector")

        # URLs must be http(s)
        if 'urls' in config:
            for url in config['urls']:
                if not (url.startswith('http://') or url.startswith('https://')):
                    self.errors.append(f"URL must be http(s): {url}")

        return self.errors

    def is_valid(self, config_path):
        return len(self.validate(config_path)) == 0
