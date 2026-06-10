import sqlite3
from typing import List


class Database:
    def __init__(self, db_path: str = "./data/gym_bot.db"):
        self.db_path = db_path
        self._init_db()

    def _connect(self):
        return sqlite3.connect(self.db_path)

    def _init_db(self):
        with self._connect() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS events (
                    event_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    channel_id INTEGER NOT NULL,
                    message_id INTEGER,
                    date TEXT NOT NULL,
                    time TEXT NOT NULL,
                    participants TEXT DEFAULT '',
                    drivers TEXT DEFAULT ''
                )
            """)

    def create_event(self, channel_id: int, date: str, time: str) -> int:
        with self._connect() as conn:
            cur = conn.execute(
                "INSERT INTO events (channel_id, date, time) VALUES (?, ?, ?)",
                (channel_id, date, time)
            )
            return cur.lastrowid

    def get_event(self, event_id: int):
        with self._connect() as conn:
            return conn.execute(
                "SELECT * FROM events WHERE event_id = ?",
                (event_id,)
            ).fetchone()

    def get_all_events(self):
      with self._connect() as conn:
        return conn.execute(
          "SELECT event_id FROM events"
        ).fetchall()

    def update_message(self, event_id: int, message_id: int):
        with self._connect() as conn:
            conn.execute(
                "UPDATE events SET message_id = ? WHERE event_id = ?",
                (message_id, event_id)
            )

    def update(self, event_id: int, participants: List[str], drivers: List[str]):
        with self._connect() as conn:
            conn.execute("""
                UPDATE events
                SET participants = ?, drivers = ?
                WHERE event_id = ?
            """, (
                ",".join(participants),
                ",".join(drivers),
                event_id
            ))