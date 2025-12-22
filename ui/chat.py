import streamlit as st
import time

from ui.renderer import render_result
from ui.state import init_chat_state, get_active_chat

from core.suggestions.initial import INITIAL_QUESTIONS
from core.suggestions.followups import suggest_followups
from core.results.classifier import build_result_profile

# ✅ LLM follow-ups
from core.llm.followups import generate_followups_llm
from core.llm.ollama import get_chart_llm

_followup_llm = get_chart_llm()


def render_chat(agent):
    init_chat_state()

    # ---- Sidebar: Chat sessions ----
    with st.sidebar:
        st.markdown("## 💬 Chats")

        # New Chat
        if st.button("➕ New Chat"):
            import uuid, time as _time

            chat_id = str(uuid.uuid4())
            st.session_state.chats[chat_id] = {
                "name": "New Chat",
                "created_at": _time.time(),
                "history": [],
            }
            st.session_state.active_chat_id = chat_id
            st.rerun()

        st.divider()

        # 🔍 Search chats
        search_query = st.text_input(
            "🔍 Search chats",
            placeholder="Type to filter chats…",
        ).lower()

        # ---- Chat list ----
        for cid, chat in st.session_state.chats.items():
            name = chat["name"]

            if search_query and search_query not in name.lower():
                continue

            label = name
            if cid == st.session_state.active_chat_id:
                label = f"➡️ {label}"

            if st.button(label, key=f"chat_{cid}"):
                st.session_state.active_chat_id = cid
                st.rerun()

        st.divider()

        # ✏️ Rename active chat (explicit confirm)
        active_chat_id = st.session_state.active_chat_id
        active_chat = st.session_state.chats[active_chat_id]

        draft_name = st.text_input(
            "✏️ Rename chat",
            value=active_chat["name"],
            key=f"rename_draft_{active_chat_id}",
        )

        if st.button("✅ Confirm rename"):
            if draft_name.strip():
                active_chat["name"] = draft_name.strip()
                st.rerun()

                st.divider()
        st.markdown("### ⚠️ Danger Zone")

        # ---- Delete current chat ----
        delete_current = st.checkbox("I understand, delete current chat")

        if st.button("🗑️ Delete Current Chat", disabled=not delete_current):
            current_id = st.session_state.active_chat_id
            st.session_state.chats.pop(current_id, None)

            # If no chats left, create a fresh one
            if not st.session_state.chats:
                import uuid, time as _time
                new_id = str(uuid.uuid4())
                st.session_state.chats[new_id] = {
                    "name": "New Chat",
                    "created_at": _time.time(),
                    "history": [],
                }
                st.session_state.active_chat_id = new_id
            else:
                # Switch to any remaining chat
                st.session_state.active_chat_id = next(
                    iter(st.session_state.chats.keys())
                )

            st.rerun()

        st.divider()

        # ---- Delete all chats ----
        delete_all = st.checkbox("I understand, delete ALL chats")

        if st.button("🚨 Delete ALL Chats", disabled=not delete_all):
            st.session_state.chats.clear()

            import uuid, time as _time
            new_id = str(uuid.uuid4())
            st.session_state.chats[new_id] = {
                "name": "New Chat",
                "created_at": _time.time(),
                "history": [],
            }
            st.session_state.active_chat_id = new_id

            st.rerun()

    # ---- Active chat reference ----
    chat = get_active_chat()

    # ---- Clear Chat (CURRENT CHAT ONLY) ----
    if st.button("🧹 Clear chat"):
        chat["history"] = []
        st.rerun()

    # ---- Initial suggestions (ONLY when chat is empty) ----
    if len(chat["history"]) == 0:
        st.markdown("### Try asking:")
        for q in INITIAL_QUESTIONS:
            if st.button(q, key=f"init_{q}"):
                st.session_state.pending_question = q
                st.rerun()

    # ---- Render previous interactions (ONLY source of truth) ----
    for entry in chat["history"]:
        with st.chat_message("user"):
            st.markdown(entry["question"])

        with st.chat_message("assistant"):
            render_result(entry["result"])

            if entry.get("duration") is not None:
                st.caption(f"⏱️ Processed in {entry['duration']} seconds")

            # ---- Follow-up suggestions (LLM → fallback) ----
            profile = build_result_profile(entry["result"]["data"])

            followups = generate_followups_llm(
                llm=_followup_llm,
                question=entry["question"],
                profile=profile,
            )

            if not followups:
                followups = suggest_followups(entry["question"], profile)

            if followups:
                st.markdown("**You might also ask:**")
                for fq in followups:
                    if st.button(fq, key=f"{entry['question']}_{fq}"):
                        st.session_state.pending_question = fq
                        st.rerun()

    # ---- Determine next question (typed OR suggested) ----
    question = st.session_state.pop("pending_question", None) or st.chat_input(
        "Ask a business question…"
    )

    if question:
        with st.chat_message("user"):
            st.markdown(question)

        start_time = time.perf_counter()

        with st.spinner("Analyzing data..."):
            result = agent(question)

        duration = round(time.perf_counter() - start_time, 2)

        result["question"] = question

        # ---- Auto-name chat on first question ----
        if len(chat["history"]) == 0:
            chat["name"] = question[:40]

        chat["history"].append(
            {
                "question": question,
                "result": result,
                "duration": duration,
            }
        )

        st.rerun()