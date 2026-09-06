from src import cli


def test_main_without_command_returns_non_zero(capsys):
    exit_code = cli.main([])

    captured = capsys.readouterr()
    assert exit_code == cli.EXIT_GENERAL
    assert "usage:" in captured.out


def test_list_sites_works_outside_repo_root(monkeypatch, tmp_path, capsys):
    monkeypatch.chdir(tmp_path)
    exit_code = cli.main(["list-sites"])

    captured = capsys.readouterr()
    assert exit_code == cli.EXIT_OK
    assert "quotes" in captured.out


def test_validate_all_reports_success(capsys):
    exit_code = cli.main(["validate-all"])

    captured = capsys.readouterr()
    assert exit_code == cli.EXIT_OK
    assert "quotes: Valid" in captured.out


def test_run_site_missing_config_returns_config_error(monkeypatch, tmp_path):
    monkeypatch.delenv("SLACK_WEBHOOK_URL", raising=False)
    exit_code = cli.run_site("missing", demo_mode=True, sites_dir=tmp_path)

    assert exit_code == cli.EXIT_CONFIG


def test_failed_sheets_delivery_can_be_retried_without_data_loss(monkeypatch, tmp_path):
    import json
    from unittest.mock import Mock

    monkeypatch.chdir(tmp_path)
    monkeypatch.delenv("SLACK_WEBHOOK_URL", raising=False)
    config = {"name": "retry", "dedupe_keys": ["id"], "min_rows": 1,
              "dedupe_db_path": str(tmp_path / "dedupe.db"),
              "output": {"csv_dir": str(tmp_path)}}
    (tmp_path / "retry.yaml").write_text(json.dumps(config))
    monkeypatch.setattr(cli.ConfigLoader, "load", lambda *_: config)
    monkeypatch.setattr(cli.Scraper, "scrape", lambda *_args, **_kwargs: [{"id": "1"}])
    exporter = Mock()
    exporter.export.side_effect = [False, True]
    monkeypatch.setattr(cli, "SheetsExporter", lambda *_: exporter)
    assert cli.run_site("retry", sites_dir=tmp_path) == cli.EXIT_RUNTIME
    assert cli.run_site("retry", sites_dir=tmp_path) == cli.EXIT_OK
    assert cli.run_site("retry", sites_dir=tmp_path) == cli.EXIT_OK
    assert exporter.export.call_count == 2
    assert exporter.export.call_args.args[0] == [{"id": "1"}]
