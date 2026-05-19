import sqlite3, json, os
from datetime import datetime
from pathlib import Path

DB_PATH = Path.home() / "aethorforge/data/memory.db"

class VectorMemory:
    def __init__(self):
        DB_PATH.parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(str(DB_PATH))
        self.conn.execute("""CREATE TABLE IF NOT EXISTS memory (
            id TEXT PRIMARY KEY,
            content TEXT,
            domain TEXT,
            timestamp TEXT
        )""")
        self.conn.commit()
        print("✓ Vector Memory online")

    def store(self, content: str, domain: str = "general"):
        self.conn.execute(
            "INSERT OR REPLACE INTO memory VALUES (?,?,?,?)",
            (str(hash(content)), content, domain,
             datetime.now().isoformat()))
        self.conn.commit()

    def recall(self, domain: str = "general", limit: int = 3):
        cur = self.conn.execute(
            "SELECT content, timestamp FROM memory WHERE domain=? ORDER BY timestamp DESC LIMIT ?",
            (domain, limit))
        return [{"content": r[0], "time": r[1]} for r in cur.fetchall()]

    def search(self, keyword: str, limit: int = 5):
        cur = self.conn.execute(
            "SELECT content, domain, timestamp FROM memory WHERE content LIKE ? LIMIT ?",
            (f"%{keyword}%", limit))
        return [{"content": r[0], "domain": r[1], "time": r[2]} for r in cur.fetchall()]

    def stats(self) -> dict:
        cur = self.conn.execute("SELECT COUNT(*), domain FROM memory GROUP BY domain")
        return {r[1]: r[0] for r in cur.fetchall()}

if __name__ == "__main__":
    m = VectorMemory()
    m.store("IDOR found on /api/users/123", "bounty")
    m.store("SaaS login recon complete", "pentest")
    print(m.recall("bounty"))
    print(m.stats())
