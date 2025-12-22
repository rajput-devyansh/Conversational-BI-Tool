import streamlit as st
from core.results.classifier import build_result_profile
from core.results.chart_eligibility import get_eligible_charts
from ui.explainability import render_explainability_panel
from core.llm.chart_selector import select_chart_type
from core.llm.ollama import get_chart_llm
from core.results.types import ResultType
from ui.summary import render_executive_summary
from ui.charts import (
    render_metric,
    render_time_series,
    render_categorical,
    render_table,
    render_empty,
)

_chart_llm = get_chart_llm()


def render_result(result: dict):
    if not result["success"]:
        st.error(result["error"])
        return

    df = result["data"]

    # 🔑 NEW: build semantic profile
    profile = build_result_profile(df)
    result_type = profile.result_type
    eligible_charts = get_eligible_charts(profile)

    # ---- EMPTY ----
    if result_type == ResultType.EMPTY:
        render_empty()
        render_explainability_panel(result)
        return

    # ---- METRIC (deterministic) ----
    if result_type == ResultType.METRIC:
        render_metric(df)

    # ---- TIME SERIES (deterministic) ----
    elif result_type == ResultType.TIME_SERIES:
        render_time_series(df, profile)

    # ---- AMBIGUOUS: AI chooses among eligible charts ----
    elif result_type in {ResultType.CATEGORICAL, ResultType.TABULAR}:
        chart_choice = select_chart_type(
            _chart_llm,
            result.get("question", ""),
            profile,
            eligible_charts,
        )

        print(f"LLM selected chart type: {chart_choice}")
        print(f"Eligible charts: {eligible_charts}")

        if chart_choice == "bar":
            render_categorical(df, profile)
        elif chart_choice == "line":
            render_time_series(df, profile)
        elif chart_choice == "metric":
            render_metric(df)
        else:
            render_table(df)
    
    # ---- Executive summary ----
    render_executive_summary(
        df=df,
        profile=profile,
        question=result.get("question", ""),
    )

    # ---- EXPLAINABILITY ----
    render_explainability_panel(result)