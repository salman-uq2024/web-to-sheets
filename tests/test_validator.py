import yaml

from src.qa.validator import SchemaValidator


def test_validator_flags_missing_required_fields(tmp_path):
    config_path = tmp_path / "invalid.yaml"
    config_path.write_text(yaml.dump({
        "name": "example",
        "urls": ["https://example.com"],
        # selectors intentionally omitted
        "pagination": {"type": "none"},
        "dedupe_keys": ["id"],
        "output": {"sheet_tab": "Sheet1"},
        "min_rows": 1,
    }))

    validator = SchemaValidator()
    errors = validator.validate(str(config_path))

    assert any("selectors" in error for error in errors)


def test_validator_accepts_optional_demo_fields(tmp_path):
    config_path = tmp_path / "valid.yaml"
    config_path.write_text(yaml.dump({
        "name": "example",
        "urls": ["https://example.com"],
        "selectors": {"item": ".row", "id": ".row-id"},
        "pagination": {"type": "none"},
        "dedupe_keys": ["id"],
        "output": {
            "sheet_tab": "Sheet1",
            "csv_dir": "out",
            "columns": ["id"],
        },
        "min_rows": 1,
        "demo_fixture": "docs/fixtures/sample.html",
        "allowed_domains": ["example.com"],
    }))

    validator = SchemaValidator()
    assert validator.is_valid(str(config_path))


def test_validator_allows_csv_only_output(tmp_path):
    config_path = tmp_path / "csv_only.yaml"
    config_path.write_text(yaml.dump({
        "name": "example",
        "urls": ["https://example.com"],
        "selectors": {"item": ".row", "id": ".row-id"},
        "pagination": {"type": "none"},
        "dedupe_keys": ["id"],
        "output": {"csv_dir": "out"},
        "min_rows": 1,
    }))

    validator = SchemaValidator()
    assert validator.is_valid(str(config_path))


def test_validator_accepts_file_urls(tmp_path):
    config_path = tmp_path / "file_url.yaml"
    config_path.write_text(yaml.dump({
        "name": "example",
        "urls": ["file:///tmp/fixture.html"],
        "selectors": {"item": ".row", "id": ".row-id"},
        "pagination": {"type": "none"},
        "dedupe_keys": ["id"],
        "output": {"csv_dir": "out"},
        "min_rows": 0,
    }))

    validator = SchemaValidator()
    assert validator.is_valid(str(config_path))


def test_validator_rejects_invalid_min_rows_and_dedupe_keys(tmp_path):
    config_path = tmp_path / "bad_ranges.yaml"
    config_path.write_text(yaml.dump({
        "name": "example",
        "urls": ["https://example.com"],
        "selectors": {"item": ".row", "id": ".row-id"},
        "pagination": {"type": "none"},
        "dedupe_keys": [],
        "output": {"csv_dir": "out"},
        "min_rows": -1,
    }))

    validator = SchemaValidator()
    errors = validator.validate(str(config_path))

    assert any("dedupe_keys must be a non-empty list" in error for error in errors)
    assert any("min_rows must be a non-negative integer" in error for error in errors)
