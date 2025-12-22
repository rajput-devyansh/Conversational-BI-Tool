import streamlit as st
import time

from ui.renderer import render_result
from ui.state import init_chat_state


def render_chat(agent):
    init_chat_state()

    # ---- Initialize chat history if missing ----
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    # ---- Render previous interactions (ONLY source of truth) ----
    for entry in st.session_state.chat_history:
        with st.chat_message("user"):
            st.markdown(entry["question"])

        with st.chat_message("assistant"):
            render_result(entry["result"])

            if entry.get("duration") is not None:
                st.caption(f"⏱️ Processed in {entry['duration']} seconds")

    # ---- New user input ----
    question = st.chat_input("Ask a business question…")

    if question:
        # Show user message immediately
        with st.chat_message("user"):
            st.markdown(question)

        # Measure end-to-end time
        start_time = time.perf_counter()

        with st.spinner("Analyzing data..."):
            result = agent(question)

        duration = round(time.perf_counter() - start_time, 2)

        # Attach question for downstream use
        result["question"] = question

        # Store interaction ONLY (do not render here)
        st.session_state.chat_history.append(
            {
                "question": question,
                "result": result,
                "duration": duration,
            }
        )

        # Force rerun so history loop renders it exactly once
        st.rerun()