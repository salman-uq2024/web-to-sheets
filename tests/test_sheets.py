import pytest

from src.core.sheets import SheetsExporter


class StubLogger:
    def __init__(self):
        self.infos = []
        self.errors = []

    def info(self, message):
        self.infos.append(message)

    def error(self, message):
        self.errors.append(message)


@pytest.fixture(autouse=True)
def clear_env(monkeypatch):
    monkeypatch.delenv('GOOGLE_SHEETS_ID', raising=False)
    monkeypatch.delenv('GOOGLE_SHEETS_CREDENTIALS_PATH', raising=False)
    monkeypatch.delenv('SHEET_ID', raising=False)
    monkeypatch.delenv('SHEETS_CREDENTIALS_PATH', raising=False)
    monkeypatch.delenv('SERVICE_ACCOUNT_JSON', raising=False)
    yield


def test_exporter_skips_when_not_configured(monkeypatch):
    logger = StubLogger()
    exporter = SheetsExporter({'output': {'sheet_tab': 'Sheet1'}}, logger)

    exporter.export([{'a': 1}])

    assert exporter.gc is None
    assert any('Sheets exporter not configured' in msg for msg in logger.infos)


def test_exporter_initialises_client(tmp_path, monkeypatch, mocker):
    creds = tmp_path / 'creds.json'
    creds.write_text('{}')

    monkeypatch.setenv('GOOGLE_SHEETS_ID', 'sheet-id-123')
    monkeypatch.setenv('GOOGLE_SHEETS_CREDENTIALS_PATH', str(creds))

    logger = StubLogger()
    config = {'output': {'sheet_tab': 'Sheet1', 'columns': ['alpha', 'beta']}}

    client_mock = mocker.Mock()
    worksheet_mock = mocker.Mock()
    client_mock.open_by_key.return_value.worksheet.return_value = worksheet_mock
    mocker.patch('src.core.sheets.gspread.service_account', return_value=client_mock)

    exporter = SheetsExporter(config, logger)
    exporter.export([{'alpha': '1', 'beta': '2'}])

    client_mock.open_by_key.assert_called_once_with('sheet-id-123')
    worksheet_mock.append_rows.assert_called_once_with([["1", "2"]])


def test_exporter_uses_columns_order(monkeypatch, tmp_path, mocker):
    creds = tmp_path / 'creds.json'
    creds.write_text('{}')

    monkeypatch.setenv('GOOGLE_SHEETS_ID', 'sheet-id-123')
    monkeypatch.setenv('GOOGLE_SHEETS_CREDENTIALS_PATH', str(creds))

    logger = StubLogger()
    config = {'output': {'sheet_tab': 'Sheet1', 'columns': ['beta', 'alpha']}}

    client_mock = mocker.Mock()
    worksheet_mock = mocker.Mock()
    client_mock.open_by_key.return_value.worksheet.return_value = worksheet_mock
    mocker.patch('src.core.sheets.gspread.service_account', return_value=client_mock)

    exporter = SheetsExporter(config, logger)
    exporter.export([{'alpha': '1', 'beta': '2'}])

    worksheet_mock.append_rows.assert_called_once_with([["2", "1"]])
