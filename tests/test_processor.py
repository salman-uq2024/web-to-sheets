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


def test_duplicate_rows_in_one_batch_are_exported_once(tmp_path):
    processor = DataProcessor(build_config(tmp_path), StubLogger(), demo_mode=True)
    assert processor.process([{"id": "1"}, {"id": "1"}]) == [{"id": "1"}]


def test_list_valued_dedupe_keys_remain_supported(tmp_path):
    processor = DataProcessor(build_config(tmp_path), StubLogger(), demo_mode=True)
    rows = [{"id": ["one", "two"]}, {"id": ["one", "two"]}]
    assert processor.process(rows) == rows[:1]


def test_csv_failure_does_not_consume_rows(tmp_path, monkeypatch):
    processor = DataProcessor(build_config(tmp_path), StubLogger(), demo_mode=True)
    original_write = processor.write_csv

    def fail(_data):
        raise OSError("disk full")

    monkeypatch.setattr(processor, "write_csv", fail)
    with pytest.raises(OSError):
        processor.process([{"id": "1"}])
    monkeypatch.setattr(processor, "write_csv", original_write)
    assert processor.process([{"id": "1"}]) == [{"id": "1"}]


def test_deferred_delivery_remains_retryable_until_acknowledged(tmp_path):
    processor = DataProcessor(build_config(tmp_path), StubLogger(), demo_mode=True)
    rows = [{"id": "1"}]
    assert processor.process(rows, commit=False) == rows
    assert processor.process(rows, commit=False) == rows
    processor.mark_delivered(rows)
    assert processor.process(rows, commit=False) == []
