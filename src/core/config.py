import yaml
from ..qa.validator import SchemaValidator


class ConfigLoader:
    def __init__(self, validator=None):
        self.validator = validator or SchemaValidator()

    def load(self, config_path):
        if not self.validator.is_valid(config_path):
            raise ValueError(f"Invalid config: {self.validator.errors}")

        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)

        # Apply defaults
        config.setdefault('rate_limit', {'rps': 1, 'burst': 2})
        config.setdefault('timeouts', {'connect': 10, 'read': 20})
        config.setdefault('headers', {})
        config.setdefault('cookies', {})
        config.setdefault('auth', {'type': 'none'})

        return config
