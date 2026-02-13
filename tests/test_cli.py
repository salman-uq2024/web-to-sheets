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
