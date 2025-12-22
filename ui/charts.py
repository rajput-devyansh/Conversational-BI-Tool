import streamlit as st
import pandas as pd


def render_metric(df: pd.DataFrame):
    value = df.iloc[0, 0]
    label = df.columns[0].replace("_", " ").title()
    st.metric(label=label, value=f"{value:,.2f}")


def render_time_series(df: pd.DataFrame):
    time_col = df.columns[0]
    st.line_chart(df.set_index(time_col))


def render_categorical(df: pd.DataFrame):
    category_col = df.columns[0]
    st.bar_chart(df.set_index(category_col))


def render_table(df: pd.DataFrame):
    st.dataframe(df, width="stretch")


def render_empty():
    st.info("No data found for this query.")