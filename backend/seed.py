from datetime import datetime, timezone
from pathlib import Path
import sqlite3

DB_PATH = Path(__file__).parent / "data" / "nagrik_seva.sqlite3"
DB_PATH.parent.mkdir(exist_ok=True)
with sqlite3.connect(DB_PATH) as db:
    schema = (Path(__file__).parent / "schema.sql").read_text()
    db.executescript(schema)
    db.executemany("INSERT OR IGNORE INTO departments(name, sla_hours) VALUES (?, ?)", [("Electrical maintenance", 48), ("Water works", 24), ("Sanitation", 24), ("Ward operations", 72)])
    db.executemany("INSERT OR IGNORE INTO wards(id, name, city) VALUES (?, ?, ?)", [(18, "Ward 18 · Jubilee Hills", "Hyderabad"), (19, "Ward 19 · Shaikpet", "Hyderabad")])
    print(f"Seeded Nagrik Seva at {datetime.now(timezone.utc).isoformat()}")
