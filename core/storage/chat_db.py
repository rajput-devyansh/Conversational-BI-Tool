import sqlite3
import json
import time
from pathlib import Path

DB_PATH = Path("data/chats.db")


def get_conn():
    DB_PATH.parent.mkdir(exist_ok=True)
    return sqlite3.connect(DB_PATH)


def init_db():
    conn = get_conn()
    cur = conn.cursor()

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS chats (
            id TEXT PRIMARY KEY,
            name TEXT,
            created_at REAL
        )
        """
    )

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            chat_id TEXT,
            role TEXT,
            content TEXT,
            result_json TEXT,
            duration REAL,
            created_at REAL
        )
        """
    )

    conn.commit()
    conn.close()


# ---------- LOAD ----------

def load_chats():
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("SELECT id, name, created_at FROM chats ORDER BY created_at")
    rows = cur.fetchall()

    chats = {}
    for chat_id, name, created_at in rows:
        chats[chat_id] = {
            "name": name,
            "created_at": created_at,
            "history": load_messages(chat_id),
        }

    conn.close()
    return chats


def load_messages(chat_id):
    conn = get_conn()
    cur = conn.cursor()

    cur.execute(
        """
        SELECT role, content, result_json, duration
        FROM messages
        WHERE chat_id = ?
        ORDER BY created_at
        """,
        (chat_id,),
    )

    messages = []
    for role, content, result_json, duration in cur.fetchall():
        entry = {
            "question": content if role == "user" else None,
            "result": json.loads(result_json) if result_json else None,
            "duration": duration,
        }
        messages.append(entry)

    conn.close()
    return messages


# ---------- SAVE ----------

def save_chat(chat_id, name):
    conn = get_conn()
    cur = conn.cursor()

    cur.execute(
        """
        INSERT OR REPLACE INTO chats (id, name, created_at)
        VALUES (?, ?, ?)
        """,
        (chat_id, name, time.time()),
    )

    conn.commit()
    conn.close()


def save_message(chat_id, role, content, result=None, duration=None):
    conn = get_conn()
    cur = conn.cursor()

    cur.execute(
        """
        INSERT INTO messages (chat_id, role, content, result_json, duration, created_at)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (
            chat_id,
            role,
            content,
            json.dumps(result) if result else None,
            duration,
            time.time(),
        ),
    )

    conn.commit()
    conn.close()


# ---------- DELETE ----------

def delete_chat(chat_id):
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("DELETE FROM messages WHERE chat_id = ?", (chat_id,))
    cur.execute("DELETE FROM chats WHERE id = ?", (chat_id,))

    conn.commit()
    conn.close()


def delete_all_chats():
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("DELETE FROM messages")
    cur.execute("DELETE FROM chats")

    conn.commit()
    conn.close()