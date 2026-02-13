import yaml

from ..qa.validator import SchemaValidator


class ConfigLoader:
    def __init__(self, validator=None):
        self.validator = validator or SchemaValidator()

    def load(self, config_path):
        if not self.validator.is_valid(config_path):
            raise ValueError(f"Invalid config: {self.validator.errors}")

        with open(config_path, "r", encoding="utf-8") as f:
            config = yaml.safe_load(f)

        if not isinstance(config, dict):
            raise ValueError("Invalid config: top-level YAML must be a mapping")

        # Apply defaults
        rate_limit = config.setdefault("rate_limit", {})
        rate_limit.setdefault("rps", 1)
        rate_limit.setdefault("burst", 2)

        timeouts = config.setdefault("timeouts", {})
        timeouts.setdefault("connect", 10)
        timeouts.setdefault("read", 20)

        headers = config.setdefault("headers", {})
        headers.setdefault("User-Agent", "web-to-sheets/0.1")

        config.setdefault("cookies", {})
        config.setdefault("auth", {"type": "none"})
        config.setdefault("respect_robots", True)
        config.setdefault("output", {})
        config.setdefault("allowed_domains", [])

        return config
