import csv
import os
from pathlib import Path

from .database import DedupeDB, InMemoryDedupeDB


class DataProcessor:
    def __init__(self, config, logger, demo_mode=False, db=None):
        self.config = config
        self.logger = logger
        self.demo_mode = demo_mode
        if db is not None:
            self.db = db
        elif demo_mode:
            self.db = InMemoryDedupeDB()
        else:
            db_path = config.get("dedupe_db_path") or os.getenv("DEDUPE_DB_PATH", "dedupe.db")
            self.db = DedupeDB(db_path=db_path)

    def process(self, data):
        deduped_data = []
        pending_marks = []
        for item in data:
            dedupe_key = self._build_dedupe_key(item)
            if not self.db.is_deduped(self.config['name'], dedupe_key):
                deduped_data.append(item)
                pending_marks.append(dedupe_key)

        if len(deduped_data) < self.config['min_rows']:
            if pending_marks:
                # We gathered new rows but did not hit the configured threshold.
                raise ValueError(f"Insufficient data: {len(deduped_data)} < {self.config['min_rows']}")

            if data:
                self.logger.info("No new unique rows found; skipping export")
                return []

            raise ValueError(f"Insufficient data: {len(deduped_data)} < {self.config['min_rows']}")

        for dedupe_key in pending_marks:
            self.db.mark_deduped(self.config['name'], dedupe_key)

        self.write_csv(deduped_data)
        return deduped_data

    def write_csv(self, data):
        if not data:
            return

        filename = f"{self.config['name']}.csv"
        output_cfg = self.config.get('output', {})
        output_dir = output_cfg.get('csv_dir')
        columns = output_cfg.get('columns')

        if columns is not None:
            if not isinstance(columns, list) or not all(isinstance(col, str) for col in columns):
                raise ValueError('output.columns must be a list of column names when provided')
        else:
            columns = list(data[0].keys())

        if output_dir:
            file_path = Path(output_dir) / filename
            file_path.parent.mkdir(parents=True, exist_ok=True)
        else:
            file_path = Path(filename)
        with open(file_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=columns)
            writer.writeheader()
            formatted_rows = [
                {column: item.get(column, "") for column in columns}
                for item in data
            ]
            writer.writerows(formatted_rows)
        self.logger.info(f"CSV written: {file_path}")

    def _build_dedupe_key(self, item: dict) -> tuple:
        missing_keys = [key for key in self.config["dedupe_keys"] if key not in item]
        if missing_keys:
            raise ValueError(
                f"Scraped item missing dedupe key(s): {', '.join(missing_keys)}. "
                "Check selectors and dedupe_keys configuration."
            )
        return tuple(item[key] for key in self.config["dedupe_keys"])
