import sqlite3
import os
from datetime import datetime

class DatabaseManager:
    def __init__(self, db_path):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        # Ensure directory exists
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS usage_history (
                    key_hash TEXT,
                    date TEXT,
                    usage REAL,
                    PRIMARY KEY (key_hash, date)
                )
            """)
            conn.commit()

    def log_usage(self, key_hash, usage):
        date_str = datetime.utcnow().strftime('%Y-%m-%d')
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT OR REPLACE INTO usage_history (key_hash, date, usage)
                VALUES (?, ?, ?)
            """, (key_hash, date_str, usage))
            conn.commit()

    def get_last_7_days_usage(self, key_hash):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                SELECT usage FROM usage_history
                WHERE key_hash = ?
                ORDER BY date DESC
                LIMIT 7
            """, (key_hash,))
            return [row[0] for row in cursor.fetchall()]

