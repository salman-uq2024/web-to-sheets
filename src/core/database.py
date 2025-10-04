import hashlib
import sqlite3


class InMemoryDedupeDB:
    """Ephemeral dedupe store for demo mode and tests."""

    def __init__(self):
        self._seen = {}

    def is_deduped(self, site, dedupe_key):
        key_hash = hashlib.md5(str(dedupe_key).encode()).hexdigest()
        return key_hash in self._seen.get(site, set())

    def mark_deduped(self, site, dedupe_key):
        key_hash = hashlib.md5(str(dedupe_key).encode()).hexdigest()
        self._seen.setdefault(site, set()).add(key_hash)


class DedupeDB:
    def __init__(self, db_path='dedupe.db'):
        self.db_path = db_path
        self.init_db()

    def init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS deduped (
                    site TEXT,
                    key_hash TEXT,
                    PRIMARY KEY (site, key_hash)
                )
            ''')

    def is_deduped(self, site, dedupe_key):
        key_hash = hashlib.md5(str(dedupe_key).encode()).hexdigest()
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT 1 FROM deduped WHERE site = ? AND key_hash = ?',
                           (site, key_hash))
            return cursor.fetchone() is not None

    def mark_deduped(self, site, dedupe_key):
        key_hash = hashlib.md5(str(dedupe_key).encode()).hexdigest()
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('INSERT OR IGNORE INTO deduped (site, key_hash) VALUES (?, ?)',
                         (site, key_hash))
