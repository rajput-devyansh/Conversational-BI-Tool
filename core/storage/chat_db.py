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

def load_chats():
    """
    Load all chats and their messages from the database.
    Returns a dict compatible with st.session_state.chats.
    """
    conn = get_connection()
    cur = conn.cursor()

    # Load chats
    cur.execute("SELECT id, name, created_at FROM chats")
    chats_rows = cur.fetchall()

    chats = {}

    for chat_id, name, created_at in chats_rows:
        chats[chat_id] = {
            "name": name,
            "created_at": created_at,
            "history": [],
        }

    # Load messages
    cur.execute("""
        SELECT chat_id, question, result_json, duration, created_at
        FROM messages
        ORDER BY created_at ASC
    """)
    message_rows = cur.fetchall()

    for chat_id, question, result_json, duration, created_at in message_rows:
        if chat_id not in chats:
            continue

        try:
            result = json.loads(result_json)
        except Exception:
            continue

        chats[chat_id]["history"].append(
            {
                "question": question,
                "result": result,
                "duration": duration,
                "created_at": created_at,
            }
        )

    conn.close()
    return chats