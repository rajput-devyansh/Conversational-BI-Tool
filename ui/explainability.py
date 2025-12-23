import streamlit as st
from core.sql.inspection import extract_tables_from_sql

def render_explainability_panel(result: dict):
    with st.expander("🔍 Technical details"):
        # SQL
        st.markdown("**Generated SQL**")
        st.code(result.get("sql", ""), language="sql")

        # Execution metadata
        st.markdown("**Execution info**")
        col1, col2, col3 = st.columns(3)

        col1.metric("Success", "Yes" if result["success"] else "No")
        col2.metric("Rows Returned", _row_count(result))
        col3.metric("Attempts", result.get("attempts", 1))

        # Tables used
        tables = extract_tables_from_sql(result.get("sql", ""))
        if tables:
            st.markdown("**Tables used**")
            st.write(", ".join(tables))

def _row_count(result: dict) -> int:
    df = result.get("data")
    if df is None:
        return 0
    return len(df)