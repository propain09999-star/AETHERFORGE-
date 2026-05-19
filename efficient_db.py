import sqlite3
import zstandard as zstd
import json

class EfficientMetadataDB:
    def __init__(self, db_path="metadata.db"):
        self.conn = sqlite3.connect(db_path)
        self.conn.execute("CREATE TABLE IF NOT EXISTS metadata (id TEXT PRIMARY KEY, data BLOB, timestamp TEXT)")

    def insert_compressed(self, key: str, data: dict):
        compressed = zstd.compress(json.dumps(data).encode())
        self.conn.execute("INSERT OR REPLACE INTO metadata VALUES (?, ?, datetime('now'))", (key, compressed))
        self.conn.commit()

    def query(self, key: str) -> dict:
        row = self.conn.execute("SELECT data FROM metadata WHERE id=?", (key,)).fetchone()
        return json.loads(zstd.decompress(row[0]).decode()) if row else None
