import csv
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
            self.db = DedupeDB()

    def process(self, data):
        deduped_data = []
        pending_marks = []
        for item in data:
            dedupe_key = tuple(item[k] for k in self.config['dedupe_keys'])
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
        output_dir = self.config.get('output', {}).get('csv_dir')
        if output_dir:
            file_path = Path(output_dir) / filename
            file_path.parent.mkdir(parents=True, exist_ok=True)
        else:
            file_path = Path(filename)
        with open(file_path, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=data[0].keys())
            writer.writeheader()
            writer.writerows(data)
        self.logger.info(f"CSV written: {file_path}")
