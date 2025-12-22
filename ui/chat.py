import streamlit as st
import time

from ui.renderer import render_result
from ui.state import init_chat_state

from core.suggestions.initial import INITIAL_QUESTIONS
from core.suggestions.followups import suggest_followups
from core.results.classifier import build_result_profile

# ✅ NEW (LLM follow-ups)
from core.llm.followups import generate_followups_llm
from core.llm.ollama import get_chart_llm

_followup_llm = get_chart_llm()


def render_chat(agent):
    init_chat_state()

    # ---- Initialize chat history if missing ----
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    # ---- Clear Chat ----
    if st.button("🧹 Clear chat"):
        st.session_state.chat_history = []
        st.rerun()

    # ---- Initial suggestions (ONLY when chat is empty) ----
    if len(st.session_state.chat_history) == 0:
        st.markdown("### Try asking:")
        for q in INITIAL_QUESTIONS:
            if st.button(q, key=f"init_{q}"):
                st.session_state.pending_question = q
                st.rerun()

    # ---- Render previous interactions (ONLY source of truth) ----
    for entry in st.session_state.chat_history:
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
            print("LLM follow-ups:", followups)  # Debug print

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

        st.session_state.chat_history.append(
            {
                "question": question,
                "result": result,
                "duration": duration,
            }
        )

        st.rerun()