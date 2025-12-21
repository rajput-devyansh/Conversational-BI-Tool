import streamlit as st
from core.llm.ollama import get_ollama_llm
from core.agents.sql_agent import create_sql_agent
from ui.chat import render_chat

st.set_page_config(
    page_title="Conversational BI",
    layout="wide",
)

st.title("📊 Conversational BI Dashboard")

# Initialize LLM + agent once
@st.cache_resource
def load_agent():
    llm = get_ollama_llm()
    return create_sql_agent(llm)

agent = load_agent()

render_chat(agent)