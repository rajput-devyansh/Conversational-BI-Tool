import sqlite3
import json
import time
from pathlib import Path

DB_PATH = Path("data/chats.db")


def get_connection():
    DB_PATH.parent.mkdir(exist_ok=True)
    return sqlite3.connect(DB_PATH)


def init_db():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS chats (
        id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        created_at REAL
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        chat_id TEXT,
        question TEXT,
        result_json TEXT,
        duration REAL,
        created_at REAL,
        FOREIGN KEY (chat_id) REFERENCES chats(id)
    )
    """)

    conn.commit()
    conn.close()