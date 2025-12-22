import streamlit as st
import pandas as pd


def render_metric(df: pd.DataFrame):
    if df.empty or df.shape != (1, 1):
        st.warning("Unable to render metric for this result.")
        return

    value = df.iloc[0, 0]
    label = df.columns[0].replace("_", " ").title()

    # ---- Smart formatting ----
    if isinstance(value, (int,)) or float(value).is_integer():
        formatted_value = f"{int(value):,}"
    else:
        formatted_value = f"{value:,.2f}"

    st.metric(label=label, value=formatted_value)


def render_time_series(df: pd.DataFrame, profile):
    if not profile.temporal_cols or not profile.numeric_cols:
        st.warning("Unable to render time series for this result.")
        return

    time_col = profile.temporal_cols[0]
    value_col = profile.numeric_cols[0]

    chart_df = df[[time_col, value_col]].set_index(time_col)

    st.line_chart(chart_df)


def render_categorical(df: pd.DataFrame, profile):
    if not profile.categorical_cols or not profile.numeric_cols:
        st.warning("Unable to render categorical chart for this result.")
        return

    category_col = profile.categorical_cols[0]
    value_col = profile.numeric_cols[0]

    chart_df = df[[category_col, value_col]].set_index(category_col)

    st.bar_chart(chart_df)


def render_table(df: pd.DataFrame):
    st.dataframe(df, width="stretch")


def render_empty():
    st.info("No data found for this query.")