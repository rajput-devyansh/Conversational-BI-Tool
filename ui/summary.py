import streamlit as st
from core.results.types import ResultType
from core.results.summary_facts import extract_summary_facts
from core.llm.summary_generator import generate_executive_summary
from core.llm.ollama import get_chart_llm

_summary_llm = get_chart_llm()

def render_executive_summary(
    df,
    profile,
    question: str,
):
    """
    Render an executive summary below the chart.
    This is non-blocking and safe.
    """

    if profile.result_type in {
        ResultType.METRIC,
        ResultType.EMPTY,
    }:
        return

    facts = extract_summary_facts(
        df=df,
        profile=profile,
        question=question,
    )

    summary = generate_executive_summary(
        llm=_summary_llm,
        facts_payload=facts,
    )

    if not summary:
        return

    st.markdown("---")
    st.markdown("#### 📌 Executive Summary")
    st.markdown(summary)