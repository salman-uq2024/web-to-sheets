
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


def test_validator_flags_missing_sheet_tab(tmp_path):
    config_path = tmp_path / "invalid_output.yaml"
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
    errors = validator.validate(str(config_path))

    assert any("output.sheet_tab" in error for error in errors)
