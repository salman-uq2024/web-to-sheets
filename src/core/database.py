import hashlib
import json
import sqlite3
from pathlib import Path


def _hash_dedupe_key(dedupe_key):
    normalized = json.dumps(dedupe_key, ensure_ascii=False, sort_keys=False, separators=(",", ":"))
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()


class InMemoryDedupeDB:
    """Ephemeral dedupe store for demo mode and tests."""

    def __init__(self):
        self._seen = {}

    def is_deduped(self, site, dedupe_key):
        key_hash = _hash_dedupe_key(dedupe_key)
        return key_hash in self._seen.get(site, set())

    def mark_deduped(self, site, dedupe_key):
        key_hash = _hash_dedupe_key(dedupe_key)
        self._seen.setdefault(site, set()).add(key_hash)


class DedupeDB:
    def __init__(self, db_path="dedupe.db"):
        self.db_path = Path(db_path).expanduser()
        self.init_db()

    def init_db(self):
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        with sqlite3.connect(str(self.db_path)) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS deduped (
                    site TEXT,
                    key_hash TEXT,
                    PRIMARY KEY (site, key_hash)
                )
            """)

    def is_deduped(self, site, dedupe_key):
        key_hash = _hash_dedupe_key(dedupe_key)
        with sqlite3.connect(str(self.db_path)) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT 1 FROM deduped WHERE site = ? AND key_hash = ?",
                (site, key_hash),
            )
            return cursor.fetchone() is not None

    def mark_deduped(self, site, dedupe_key):
        key_hash = _hash_dedupe_key(dedupe_key)
        with sqlite3.connect(str(self.db_path)) as conn:
            conn.execute(
                "INSERT OR IGNORE INTO deduped (site, key_hash) VALUES (?, ?)",
                (site, key_hash),
            )
