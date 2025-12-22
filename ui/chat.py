import streamlit as st
import time
import uuid
from pathlib import Path

from ui.renderer import render_result
from ui.state import init_chat_state, get_active_chat

from core.suggestions.initial import INITIAL_QUESTIONS
from core.suggestions.followups import suggest_followups
from core.results.classifier import build_result_profile

# LLM follow-ups
from core.llm.followups import generate_followups_llm
from core.llm.ollama import get_chart_llm

# SQLite persistence
from core.storage.chat_db import (
    init_db,
    save_chat,
    save_message,
    delete_chat,
    delete_all_chats,
)

# ✅ PDF Export
from core.export.pdf_exporter import export_chat_to_pdf
from core.export.pdf_exporter import safe_filename

_followup_llm = get_chart_llm()


def render_chat(agent):
    # ---- Init DB + State ----
    init_db()
    init_chat_state()

    # =========================
    # SIDEBAR: CHAT MANAGEMENT
    # =========================
    with st.sidebar:
        st.markdown("## 💬 Chats")

        # ---- New Chat ----
        if st.button("➕ New Chat"):
            chat_id = str(uuid.uuid4())
            st.session_state.chats[chat_id] = {
                "name": "New Chat",
                "created_at": time.time(),
                "history": [],
            }
            st.session_state.active_chat_id = chat_id
            save_chat(chat_id, "New Chat")
            st.rerun()

        st.divider()

        # ---- Search Chats ----
        search_query = st.text_input(
            "🔍 Search chats",
            placeholder="Type to filter chats…",
        ).lower()

        for cid, chat in st.session_state.chats.items():
            name = chat["name"]

            if search_query and search_query not in name.lower():
                continue

            label = f"➡️ {name}" if cid == st.session_state.active_chat_id else name

            if st.button(label, key=f"chat_{cid}"):
                st.session_state.active_chat_id = cid
                st.rerun()

        st.divider()

        # ---- Rename Chat ----
        active_chat_id = st.session_state.active_chat_id
        active_chat = st.session_state.chats[active_chat_id]

        draft_name = st.text_input(
            "✏️ Rename chat",
            value=active_chat["name"],
            key=f"rename_{active_chat_id}",
        )

        if st.button("✅ Confirm rename"):
            if draft_name.strip():
                active_chat["name"] = draft_name.strip()
                save_chat(active_chat_id, active_chat["name"])
                st.rerun()

        st.divider()

        # ---- Export Chat to PDF (✅ NEW) ----
        if st.button("📄 Export chat to PDF"):
            export_dir = Path("exports")
            export_dir.mkdir(exist_ok=True)

            filename = f"{safe_filename(active_chat['name'])}.pdf"
            output_path = export_dir / filename

            export_chat_to_pdf(active_chat, output_path)

            st.success("Chat exported successfully!")
            st.download_button(
                label="⬇️ Download PDF",
                data=output_path.read_bytes(),
                file_name=filename,
                mime="application/pdf",
            )

        st.divider()
        st.markdown("### ⚠️ Danger Zone")

        # ---- Delete Current Chat ----
        confirm_delete = st.checkbox("I understand, delete current chat")

        if st.button("🗑️ Delete Current Chat", disabled=not confirm_delete):
            delete_chat(active_chat_id)
            st.session_state.chats.pop(active_chat_id, None)

            if not st.session_state.chats:
                new_id = str(uuid.uuid4())
                st.session_state.chats[new_id] = {
                    "name": "New Chat",
                    "created_at": time.time(),
                    "history": [],
                }
                save_chat(new_id, "New Chat")
                st.session_state.active_chat_id = new_id
            else:
                st.session_state.active_chat_id = next(
                    iter(st.session_state.chats.keys())
                )

            st.rerun()

        st.divider()

        # ---- Delete All Chats ----
        confirm_delete_all = st.checkbox("I understand, delete ALL chats")

        if st.button("🚨 Delete ALL Chats", disabled=not confirm_delete_all):
            delete_all_chats()
            st.session_state.chats.clear()

            new_id = str(uuid.uuid4())
            st.session_state.chats[new_id] = {
                "name": "New Chat",
                "created_at": time.time(),
                "history": [],
            }
            save_chat(new_id, "New Chat")
            st.session_state.active_chat_id = new_id
            st.rerun()

    # =========================
    # MAIN CHAT AREA
    # =========================
    chat = get_active_chat()

    # ---- Clear current chat messages ----
    if st.button("🧹 Clear chat"):
        chat["history"] = []
        delete_chat(st.session_state.active_chat_id)
        save_chat(st.session_state.active_chat_id, chat["name"])
        st.rerun()

    # ---- Initial suggestions ----
    if len(chat["history"]) == 0:
        st.markdown("### Try asking:")
        for q in INITIAL_QUESTIONS:
            if st.button(q, key=f"init_{q}"):
                st.session_state.pending_question = q
                st.rerun()

    # ---- Render history ----
    for entry in chat["history"]:
        with st.chat_message("user"):
            st.markdown(entry["question"])

        with st.chat_message("assistant"):
            render_result(entry["result"])

            if entry.get("duration") is not None:
                st.caption(f"⏱️ Processed in {entry['duration']} seconds")

            # ---- Follow-up suggestions ----
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

    # ---- Next question ----
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

        # ---- Auto-name chat ----
        if len(chat["history"]) == 0:
            chat["name"] = question[:40]
            save_chat(st.session_state.active_chat_id, chat["name"])

        # ---- Persist messages ----
        save_message(
            chat_id=st.session_state.active_chat_id,
            role="user",
            content=question,
        )

        save_message(
            chat_id=st.session_state.active_chat_id,
            role="assistant",
            content="assistant_response",
            result=result,
            duration=duration,
        )

        chat["history"].append(
            {
                "question": question,
                "result": result,
                "duration": duration,
            }
        )

        st.rerun()