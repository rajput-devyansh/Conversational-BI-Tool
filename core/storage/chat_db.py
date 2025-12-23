import sqlite3
import json
import time
from pathlib import Path
import pandas as pd

DB_PATH = Path("data/chat_data/chats.db")

def get_conn():
    DB_PATH.parent.mkdir(exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

# ---------- SERIALIZATION HELPERS ----------

def serialize_result(result: dict) -> dict:
    """
    Convert result dict into JSON-serializable form.
    """
    if result is None:
        return None

    safe = result.copy()

    df = safe.get("data")
    if isinstance(df, pd.DataFrame):
        safe["data"] = {
            "columns": list(df.columns),
            "rows": df.to_dict(orient="records"),
        }

    return safe

def deserialize_result(result_json: str) -> dict:
    """
    Restore result dict, including DataFrame.
    """
    if result_json is None:
        return None

    result = json.loads(result_json)

    data = result.get("data")
    if isinstance(data, dict) and "rows" in data:
        result["data"] = pd.DataFrame(data["rows"])

    return result

# ---------- INIT ----------

def init_db():
    conn = get_conn()
    cur = conn.cursor()

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS chats (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            created_at REAL NOT NULL
        )
        """
    )

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            chat_id TEXT NOT NULL,
            role TEXT NOT NULL,
            content TEXT,
            result_json TEXT,
            duration REAL,
            created_at REAL NOT NULL,
            FOREIGN KEY (chat_id) REFERENCES chats(id) ON DELETE CASCADE
        )
        """
    )

    conn.commit()
    conn.close()

# ---------- LOAD ----------

def load_chats():
    conn = get_conn()
    cur = conn.cursor()

    cur.execute(
        "SELECT id, name, created_at FROM chats ORDER BY created_at"
    )
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
    """
    Reconstruct full (question + result) interactions from message rows.
    """
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
    pending_question = None

    for role, content, result_json, duration in cur.fetchall():
        if role == "user":
            pending_question = content

        elif role == "assistant" and pending_question is not None:
            messages.append(
                {
                    "question": pending_question,
                    "result": deserialize_result(result_json) if result_json else None,
                    "duration": duration,
                }
            )
            pending_question = None

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
        INSERT INTO messages (
            chat_id,
            role,
            content,
            result_json,
            duration,
            created_at
        )
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (
            chat_id,
            role,
            content,
            json.dumps(serialize_result(result)) if result is not None else None,
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