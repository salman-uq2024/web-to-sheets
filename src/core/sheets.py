import os
from pathlib import Path
from typing import Iterable, List, Optional

import gspread


class SheetsExporter:
    """Export processed rows to Google Sheets when configured."""

    def __init__(self, config, logger):
        self.config = config
        self.logger = logger
        self.gc: Optional[gspread.Client] = None
        self.sheet_id: Optional[str] = None

        credentials_path = (
            os.getenv('GOOGLE_SHEETS_CREDENTIALS_PATH')
            or os.getenv('SHEETS_CREDENTIALS_PATH')
            or os.getenv('SERVICE_ACCOUNT_JSON')
            or 'service_account.json'
        )

        self.sheet_id = os.getenv('GOOGLE_SHEETS_ID') or os.getenv('SHEET_ID')

        resolved_credentials = Path(credentials_path).expanduser()

        if not self.sheet_id:
            self.logger.info('Google Sheets ID not provided; skipping Sheets export')
            return

        if not resolved_credentials.exists():
            self.logger.info(
                f"Google Sheets credentials file not found at {resolved_credentials}; skipping export"
            )
            return

        try:
            self.gc = gspread.service_account(filename=str(resolved_credentials))
        except Exception as exc:  # pragma: no cover - defensive logging
            self.logger.error(f'Failed to initialise Google Sheets client: {exc}')
            self.gc = None

    def export(self, data: Iterable[dict]):
        if not self.gc or not self.sheet_id:
            self.logger.info('Sheets exporter not configured, skipping')
            return

        sheet_tab = self.config.get('output', {}).get('sheet_tab')
        if not sheet_tab:
            self.logger.error('output.sheet_tab missing; unable to export to Google Sheets')
            return
        columns: Optional[List[str]] = self.config.get('output', {}).get('columns')

        try:
            sheet = self.gc.open_by_key(self.sheet_id).worksheet(sheet_tab)
        except Exception as exc:  # pragma: no cover - requires live Sheets
            self.logger.error(f'Failed to open Google Sheet: {exc}')
            return

        rows = self._prepare_rows(data, columns)
        if not rows:
            self.logger.info('No rows to export to Google Sheets')
            return

        try:
            sheet.append_rows(rows)
        except Exception as exc:  # pragma: no cover - requires live Sheets
            self.logger.error(f'Failed to append rows to Google Sheets: {exc}')
            return

        self.logger.info(f'Exported {len(rows)} rows to Google Sheets tab {sheet_tab}')

    @staticmethod
    def _prepare_rows(data: Iterable[dict], columns: Optional[List[str]]) -> List[List[str]]:
        prepared_rows: List[List[str]] = []
        for item in data:
            if columns:
                prepared_rows.append([str(item.get(column, '')) for column in columns])
            else:
                prepared_rows.append([str(value) for value in item.values()])
        return prepared_rows
