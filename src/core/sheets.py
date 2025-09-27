import gspread
from oauth2client.service_account import ServiceAccountCredentials
import os


class SheetsExporter:
    def __init__(self, config, logger):
        self.config = config
        self.logger = logger
        self.gc = None
        if os.getenv('SHEET_ID') and os.path.exists('service_account.json'):
            scope = ['https://spreadsheets.google.com/feeds',
                     'https://www.googleapis.com/auth/drive']
            creds = ServiceAccountCredentials.from_json_keyfile_name('service_account.json', scope)
            self.gc = gspread.authorize(creds)

    def export(self, data):
        if not self.gc:
            self.logger.info("Sheets not configured, skipping")
            return
        sheet_id = os.getenv('SHEET_ID')
        sheet = self.gc.open_by_key(sheet_id).worksheet(self.config['output']['sheet_tab'])
        # Append new rows
        rows = [list(item.values()) for item in data]
        sheet.append_rows(rows)
        self.logger.info(f"Exported {len(rows)} rows to Sheets")
