import streamlit as st
import uuid
import time

from core.storage.chat_db import init_db, load_chats


def init_chat_state():
    """
    Initialize application state.
    Loads chats from SQLite on first run.
    Safe to call multiple times.
    """

    # ---- Ensure DB & tables exist ----
    init_db()

    # ---- Load chats from DB only once ----
    if "chats" not in st.session_state:
        chats = load_chats()

        if chats:
            # Restore persisted chats
            st.session_state.chats = chats
            st.session_state.active_chat_id = next(iter(chats.keys()))
        else:
            # First-ever run: create one fresh chat
            chat_id = str(uuid.uuid4())
            st.session_state.chats = {
                chat_id: {
                    "name": "New Chat",
                    "created_at": time.time(),
                    "history": [],
                }
            }
            st.session_state.active_chat_id = chat_id


def get_active_chat():
    """
    Return the currently active chat dict.
    """
    return st.session_state.chats[st.session_state.active_chat_id]