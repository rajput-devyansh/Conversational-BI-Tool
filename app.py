import streamlit as st
from core import __init__
from ui import __init__

st.set_page_config(
    page_title="Conversational BI Dashboard",
    layout="wide"
)

st.title("📊 Conversational BI Dashboard")

st.markdown(
    """
    Ask questions about your data in natural language.
    
    _This app is under active development._
    """
)