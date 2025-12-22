import streamlit as st
import uuid
import time


def init_chat_state():
    """
    Initialize application state.
    Safe to call multiple times.
    """

    # ---- Multi-chat container ----
    if "chats" not in st.session_state:
        chat_id = str(uuid.uuid4())
        st.session_state.chats = {
            chat_id: {
                "name": "New Chat",
                "created_at": time.time(),
                "history": [],
            }
        }
        st.session_state.active_chat_id = chat_id

    # ---- Backward safety (temporary) ----
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []


def get_active_chat():
    """
    Return the currently active chat dict.
    """
    return st.session_state.chats[st.session_state.active_chat_id]