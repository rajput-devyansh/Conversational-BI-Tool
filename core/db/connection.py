import sqlite3
from pathlib import Path

DB_PATH = Path("data/Brazilian_ECommerce_Olist.db")

def get_connection():
    if not DB_PATH.exists():
        raise FileNotFoundError(
            f"Database not found at {DB_PATH}. "
            "Have you run scripts/load_data.py?"
        )

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn