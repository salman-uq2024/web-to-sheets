import pytest

from src.core.processor import DataProcessor


class StubLogger:
    def info(self, *_args, **_kwargs):
        pass

    def error(self, *_args, **_kwargs):
        pass

    def debug(self, *_args, **_kwargs):
        pass


def build_config(tmp_path):
    return {
        "name": "processor_test",
        "dedupe_keys": ["id"],
        "min_rows": 1,
        "output": {"csv_dir": str(tmp_path), "columns": ["id"]},
    }


def test_processor_raises_when_dedupe_key_missing(tmp_path):
    config = build_config(tmp_path)
    processor = DataProcessor(config, StubLogger(), demo_mode=True)

    with pytest.raises(ValueError, match="missing dedupe key"):
        processor.process([{"title": "missing id"}])


def test_processor_uses_env_dedupe_db_path(tmp_path, monkeypatch):
    db_path = tmp_path / "state" / "dedupe.db"
    monkeypatch.setenv("DEDUPE_DB_PATH", str(db_path))

    config = build_config(tmp_path)
    processor = DataProcessor(config, StubLogger(), demo_mode=False)
    processed = processor.process([{"id": "row-1"}])
    assert processed == [{"id": "row-1"}]
    assert db_path.exists()

    another_processor = DataProcessor(config, StubLogger(), demo_mode=False)
    processed_again = another_processor.process([{"id": "row-1"}])
    assert processed_again == []
