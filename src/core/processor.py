import csv
from .database import DedupeDB


class DataProcessor:
    def __init__(self, config, logger):
        self.config = config
        self.logger = logger
        self.db = DedupeDB()

    def process(self, data):
        deduped_data = []
        for item in data:
            dedupe_key = tuple(item[k] for k in self.config['dedupe_keys'])
            if not self.db.is_deduped(self.config['name'], dedupe_key):
                deduped_data.append(item)
                self.db.mark_deduped(self.config['name'], dedupe_key)

        if len(deduped_data) < self.config['min_rows']:
            raise ValueError(f"Insufficient data: {len(deduped_data)} < {self.config['min_rows']}")

        self.write_csv(deduped_data)
        return deduped_data

    def write_csv(self, data):
        if not data:
            return
        filename = f"{self.config['name']}.csv"
        with open(filename, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=data[0].keys())
            writer.writeheader()
            writer.writerows(data)
        self.logger.info(f"CSV written: {filename}")
