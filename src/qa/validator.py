import yaml
import os


class SchemaValidator:
    def __init__(self):
        self.errors = []

    def validate(self, config_path):
        # Reset per-run state so previous errors do not leak between validations
        self.errors = []

        if not os.path.exists(config_path):
            self.errors.append(f"Config file not found: {config_path}")
            return list(self.errors)

        try:
            with open(config_path, 'r') as f:
                config = yaml.safe_load(f)
        except yaml.YAMLError as e:
            self.errors.append(f"YAML parse error: {e}")
            return list(self.errors)

        if not isinstance(config, dict):
            self.errors.append("Config must be a mapping of keys to values")
            return list(self.errors)

        # Required fields
        required = ['name', 'urls', 'selectors', 'pagination', 'dedupe_keys', 'output', 'min_rows']
        for req in required:
            if req not in config:
                self.errors.append(f"Missing required field: {req}")

        if 'urls' in config and (not isinstance(config['urls'], list) or len(config['urls']) < 1):
            self.errors.append("urls must be a non-empty list")

        selectors = config.get('selectors')
        if selectors is not None:
            if not isinstance(selectors, dict):
                self.errors.append("selectors must be a mapping of field names to selectors")
            else:
                if 'item' not in selectors:
                    self.errors.append("selectors must include 'item'")
                selector_fields = [k for k in selectors if k != 'item']
                if len(selector_fields) < 1:
                    self.errors.append("selectors must have at least one field besides 'item'")
                if 'dedupe_keys' in config and not all(k in selectors for k in config['dedupe_keys']):
                    self.errors.append("dedupe_keys must reference existing selector fields")

        pagination = config.get('pagination')
        if pagination is not None:
            if not isinstance(pagination, dict):
                self.errors.append("pagination must be a mapping with pagination settings")
            else:
                pagination_type = pagination.get('type')
                if pagination_type not in ['query_param', 'next_link', 'none']:
                    self.errors.append("pagination.type must be query_param, next_link, or none")
                if pagination_type == 'query_param':
                    required_fields = {'param', 'start', 'max_pages'}
                    if not required_fields.issubset(pagination.keys()):
                        self.errors.append("pagination query_param requires param, start, max_pages")
                elif pagination_type == 'next_link':
                    if 'next_selector' not in pagination:
                        self.errors.append("pagination next_link requires next_selector")

        if 'output' in config and not isinstance(config['output'], dict):
            self.errors.append("output must be a mapping with export settings")
        elif isinstance(config.get('output'), dict):
            csv_dir = config['output'].get('csv_dir')
            if csv_dir is not None and not isinstance(csv_dir, str):
                self.errors.append("output.csv_dir must be a string path when provided")

        demo_fixture = config.get('demo_fixture')
        if demo_fixture is not None and not isinstance(demo_fixture, str):
            self.errors.append("demo_fixture must be a string path")

        allowed_domains = config.get('allowed_domains')
        if allowed_domains is not None:
            if not isinstance(allowed_domains, list) or not all(isinstance(d, str) for d in allowed_domains):
                self.errors.append("allowed_domains must be a list of domain strings")

        # URLs must be http(s)
        if 'urls' in config and isinstance(config['urls'], list):
            for url in config['urls']:
                if not (url.startswith('http://') or url.startswith('https://')):
                    self.errors.append(f"URL must be http(s): {url}")

        return list(self.errors)

    def is_valid(self, config_path):
        return len(self.validate(config_path)) == 0
