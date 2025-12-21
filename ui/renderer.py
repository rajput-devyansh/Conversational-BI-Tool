import streamlit as st
import pandas as pd

from core.results.classifier import classify_result
from core.results.types import ResultType

def render_result(result: dict):
    if not result["success"]:
        st.error(result["error"])
        return

    df = result["data"]

    result_type = classify_result(df)

    # ---- EMPTY ----
    if result_type == ResultType.EMPTY:
        st.info("No data found for this query.")
        _render_technical_details(result)
        return

    # ---- METRIC ----
    if result_type == ResultType.METRIC:
        value = df.iloc[0, 0]
        label = df.columns[0].replace("_", " ").title()
        st.metric(label=label, value=f"{value:,.2f}")

    # ---- TIME SERIES ----
    elif result_type == ResultType.TIME_SERIES:
        time_col = df.columns[0]
        st.line_chart(df.set_index(time_col))

    # ---- CATEGORICAL ----
    elif result_type == ResultType.CATEGORICAL:
        st.bar_chart(df.set_index(df.columns[0]))

    # ---- TABULAR ----
    else:
        st.dataframe(df, width="stretch")

    _render_technical_details(result)


def _render_technical_details(result: dict):
    with st.expander("🔍 Technical details"):
        st.code(result["sql"], language="sql")
        st.caption(f"Attempts: {result['attempts']}")