import sqlite3
from pathlib import Path
from datetime import datetime, timedelta

class Storage:
    """Manages the SQLite database for RAM snapshots and processes."""
    def __init__(self, db_path: Path):
        self.db_path = db_path
        self._init_db()

    def _get_conn(self):
        conn = sqlite3.connect(str(self.db_path))
        conn.execute("PRAGMA foreign_keys = ON;")
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self):
        with self._get_conn() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS snapshots (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    total_mb REAL NOT NULL,
                    available_mb REAL NOT NULL,
                    used_mb REAL NOT NULL
                )
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS processes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    snapshot_id INTEGER NOT NULL,
                    name TEXT NOT NULL,
                    pid INTEGER NOT NULL,
                    memory_mb REAL NOT NULL,
                    FOREIGN KEY (snapshot_id) REFERENCES snapshots (id) ON DELETE CASCADE
                )
            """)
            conn.commit()

    def save_snapshot(self, total: float, available: float, used: float, processes: list) -> int:
        now = datetime.now().isoformat()
        with self._get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO snapshots (timestamp, total_mb, available_mb, used_mb) VALUES (?, ?, ?, ?)",
                (now, total, available, used)
            )
            snapshot_id = cursor.lastrowid
            
            # print(f"DEBUG: saved snapshot {snapshot_id} with {len(processes)} processes")
            
            for proc in processes:
                cursor.execute(
                    "INSERT INTO processes (snapshot_id, name, pid, memory_mb) VALUES (?, ?, ?, ?)",
                    (snapshot_id, proc['name'], proc['pid'], proc['memory_mb'])
                )
            conn.commit()
            return snapshot_id

    def get_history(self, limit: int = 60) -> list:
        # Returns recent snapshots backwards in time for raw inspection
        with self._get_conn() as conn:
            rows = conn.execute(
                "SELECT id, timestamp, total_mb, available_mb, used_mb FROM snapshots ORDER BY id DESC LIMIT ?",
                (limit,)
            ).fetchall()
            return [dict(r) for r in rows]

    def get_history_chronological(self, limit: int = 60) -> list:
        # Necessary for plotting charts left-to-right
        with self._get_conn() as conn:
            rows = conn.execute(
                "SELECT timestamp, total_mb, used_mb FROM (SELECT id, timestamp, total_mb, used_mb FROM snapshots ORDER BY id DESC LIMIT ?) ORDER BY id ASC",
                (limit,)
            ).fetchall()
            return [dict(r) for r in rows]

    def get_top_offenders(self, limit: int = 10, hours: int = 24) -> list:
        # FIXME: grouping only by name averages out distinct instances but shows overall hogs.
        # Good enough for our current CLI needs.
        since_time = (datetime.now() - timedelta(hours=hours)).isoformat()
        query = """
            SELECT p.name, ROUND(AVG(p.memory_mb), 1) as avg_mb, ROUND(MAX(p.memory_mb), 1) as max_mb, COUNT(*) as seen_count
            FROM processes p
            JOIN snapshots s ON p.snapshot_id = s.id
            WHERE s.timestamp >= ?
            GROUP BY p.name
            ORDER BY avg_mb DESC
            LIMIT ?
        """
        with self._get_conn() as conn:
            rows = conn.execute(query, (since_time, limit)).fetchall()
            return [dict(r) for r in rows]
