import streamlit as st
import pandas as pd

def render_result(result: dict):
    if not result["success"]:
        st.error(result["error"])
        return

    df = result["data"]

    # ---- Empty result handling ----
    if df is None or df.empty:
        st.info("No data found for this query.")
        with st.expander("🔍 Technical details"):
            st.code(result["sql"], language="sql")
            st.caption(f"Attempts: {result['attempts']}")
        return

    # ---- KPI: single value ----
    if df.shape == (1, 1):
        value = df.iloc[0, 0]
        label = df.columns[0].replace("_", " ").title()
        st.metric(label=label, value=f"{value:,.2f}")

    # ---- Time series ----
    elif "month" in df.columns:
        st.line_chart(df.set_index("month"))

    # ---- Default table ----
    else:
        st.dataframe(df, width="stretch")

    # ---- SQL transparency ----
    with st.expander("🔍 Technical details"):
        st.code(result["sql"], language="sql")
        st.caption(f"Attempts: {result['attempts']}")