import sqlite3
from pathlib import Path
from typing import Optional

DB_PATH = Path(__file__).parent / "data" / "nagrik_seva.sqlite3"
DB_PATH.parent.mkdir(exist_ok=True)

SCHEMA = """
CREATE TABLE IF NOT EXISTS complaints (
  tracking_code TEXT PRIMARY KEY, complaint_json TEXT NOT NULL, created_at TEXT NOT NULL
)
"""

def connect():
    db = sqlite3.connect(DB_PATH)
    db.execute(SCHEMA)
    return db

def save(tracking_code: str, complaint_json: str, created_at: str) -> None:
    with connect() as db:
        db.execute("INSERT INTO complaints(tracking_code, complaint_json, created_at) VALUES (?, ?, ?)", (tracking_code, complaint_json, created_at))

def get(tracking_code: str) -> Optional[str]:
    with connect() as db:
        row = db.execute("SELECT complaint_json FROM complaints WHERE tracking_code = ?", (tracking_code,)).fetchone()
    return row[0] if row else None
