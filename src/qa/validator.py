import os

import yaml


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
            with open(config_path, "r", encoding="utf-8") as f:
                config = yaml.safe_load(f)
        except yaml.YAMLError as e:
            self.errors.append(f"YAML parse error: {e}")
            return list(self.errors)

        if not isinstance(config, dict):
            self.errors.append("Config must be a mapping of keys to values")
            return list(self.errors)

        # Required fields
        required = ["name", "urls", "selectors", "pagination", "dedupe_keys", "output", "min_rows"]
        for req in required:
            if req not in config:
                self.errors.append(f"Missing required field: {req}")

        if "name" in config and (not isinstance(config["name"], str) or not config["name"].strip()):
            self.errors.append("name must be a non-empty string")

        if "urls" in config and (not isinstance(config["urls"], list) or len(config["urls"]) < 1):
            self.errors.append("urls must be a non-empty list")

        selectors = config.get("selectors")
        selector_map = selectors if isinstance(selectors, dict) else None
        if selectors is not None:
            if not isinstance(selectors, dict):
                self.errors.append("selectors must be a mapping of field names to selectors")
            else:
                if "item" not in selectors:
                    self.errors.append("selectors must include 'item'")
                selector_fields = [k for k in selectors if k != "item"]
                if len(selector_fields) < 1:
                    self.errors.append("selectors must have at least one field besides 'item'")
                if any(not isinstance(k, str) or not k.strip() for k in selectors.keys()):
                    self.errors.append("selectors keys must be non-empty strings")
                if any(not isinstance(v, str) or not v.strip() for v in selectors.values()):
                    self.errors.append("selectors values must be non-empty CSS selector strings")
                if "dedupe_keys" in config and not all(k in selectors for k in config["dedupe_keys"]):
                    self.errors.append("dedupe_keys must reference existing selector fields")

        dedupe_keys = config.get("dedupe_keys")
        if dedupe_keys is not None:
            if not isinstance(dedupe_keys, list) or not dedupe_keys:
                self.errors.append("dedupe_keys must be a non-empty list")
            elif any(not isinstance(key, str) or not key.strip() for key in dedupe_keys):
                self.errors.append("dedupe_keys entries must be non-empty strings")

        min_rows = config.get("min_rows")
        if min_rows is not None and (not isinstance(min_rows, int) or min_rows < 0):
            self.errors.append("min_rows must be a non-negative integer")

        pagination = config.get("pagination")
        if pagination is not None:
            if not isinstance(pagination, dict):
                self.errors.append("pagination must be a mapping with pagination settings")
            else:
                pagination_type = pagination.get("type")
                if pagination_type not in ["query_param", "next_link", "none"]:
                    self.errors.append("pagination.type must be query_param, next_link, or none")
                if pagination_type == "query_param":
                    param = pagination.get("param")
                    if not isinstance(param, str) or not param.strip():
                        self.errors.append("pagination query_param requires a non-empty param")

                    start = pagination.get("start")
                    if not isinstance(start, int) or start < 1:
                        self.errors.append("pagination.start must be an integer >= 1")

                    max_pages = pagination.get("max_pages")
                    if max_pages is not None and (not isinstance(max_pages, int) or max_pages < 1):
                        self.errors.append("pagination.max_pages must be an integer >= 1 when provided")
                elif pagination_type == "next_link":
                    if "next_selector" not in pagination:
                        self.errors.append("pagination next_link requires next_selector")
                    elif (
                        not isinstance(pagination.get("next_selector"), str)
                        or not pagination["next_selector"].strip()
                    ):
                        self.errors.append("pagination.next_selector must be a non-empty string")
                    max_pages = pagination.get("max_pages")
                    if max_pages is not None and (not isinstance(max_pages, int) or max_pages < 1):
                        self.errors.append("pagination.max_pages must be an integer >= 1 when provided")

        rate_limit = config.get("rate_limit")
        if rate_limit is not None:
            if not isinstance(rate_limit, dict):
                self.errors.append("rate_limit must be a mapping")
            else:
                rps = rate_limit.get("rps")
                if rps is not None and not isinstance(rps, (int, float)):
                    self.errors.append("rate_limit.rps must be numeric when provided")
                burst = rate_limit.get("burst")
                if burst is not None and (not isinstance(burst, int) or burst < 1):
                    self.errors.append("rate_limit.burst must be an integer >= 1 when provided")

        timeouts = config.get("timeouts")
        if timeouts is not None:
            if not isinstance(timeouts, dict):
                self.errors.append("timeouts must be a mapping")
            else:
                for key in ("connect", "read"):
                    timeout = timeouts.get(key)
                    if timeout is not None and not isinstance(timeout, (int, float)):
                        self.errors.append(f"timeouts.{key} must be numeric when provided")

        if "output" in config and not isinstance(config["output"], dict):
            self.errors.append("output must be a mapping with export settings")
        elif isinstance(config.get("output"), dict):
            csv_dir = config["output"].get("csv_dir")
            if csv_dir is not None and not isinstance(csv_dir, str):
                self.errors.append("output.csv_dir must be a string path when provided")
            sheet_tab = config["output"].get("sheet_tab")
            if sheet_tab is not None and (not isinstance(sheet_tab, str) or not sheet_tab.strip()):
                self.errors.append("output.sheet_tab must be a non-empty string when provided")
            columns = config["output"].get("columns")
            if columns is not None:
                if not isinstance(columns, list) or not all(isinstance(column, str) for column in columns):
                    self.errors.append("output.columns must be a list of strings when provided")
                elif len(set(columns)) != len(columns):
                    self.errors.append("output.columns must not contain duplicates")
                elif selector_map and any(column not in selector_map for column in columns):
                    self.errors.append("output.columns must reference selector field names")

        demo_fixture = config.get("demo_fixture")
        if demo_fixture is not None and not isinstance(demo_fixture, str):
            self.errors.append("demo_fixture must be a string path")

        allowed_domains = config.get("allowed_domains")
        if allowed_domains is not None:
            if not isinstance(allowed_domains, list) or not all(isinstance(d, str) for d in allowed_domains):
                self.errors.append("allowed_domains must be a list of domain strings")

        respect_robots = config.get("respect_robots")
        if respect_robots is not None and not isinstance(respect_robots, bool):
            self.errors.append("respect_robots must be a boolean when provided")

        # URLs must be http(s) or file://
        if "urls" in config and isinstance(config["urls"], list):
            for url in config["urls"]:
                if not isinstance(url, str) or not url.strip():
                    self.errors.append(f"URL entries must be non-empty strings: {url}")
                    continue
                if not (
                    url.startswith("http://")
                    or url.startswith("https://")
                    or url.startswith("file://")
                ):
                    self.errors.append(f"URL must be http(s) or file://: {url}")

        return list(self.errors)

    def is_valid(self, config_path):
        return len(self.validate(config_path)) == 0
