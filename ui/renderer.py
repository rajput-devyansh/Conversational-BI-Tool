import streamlit as st

from core.results.classifier import classify_result
from core.results.types import ResultType
from ui.charts import (
    render_metric,
    render_time_series,
    render_categorical,
    render_table,
    render_empty,
)


def render_result(result: dict):
    if not result["success"]:
        st.error(result["error"])
        return

    df = result["data"]
    result_type = classify_result(df)

    if result_type == ResultType.EMPTY:
        render_empty()
        _render_technical_details(result)
        return

    if result_type == ResultType.METRIC:
        render_metric(df)

    elif result_type == ResultType.TIME_SERIES:
        render_time_series(df)

    elif result_type == ResultType.CATEGORICAL:
        render_categorical(df)

    else:
        render_table(df)

    _render_technical_details(result)


def _render_technical_details(result: dict):
    with st.expander("🔍 Technical details"):
        st.code(result["sql"], language="sql")
        st.caption(f"Attempts: {result['attempts']}")