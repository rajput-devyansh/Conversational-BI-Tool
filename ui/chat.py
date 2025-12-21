import streamlit as st
from ui.renderer import render_result
from ui.state import init_chat_state

def render_chat(agent):
    init_chat_state()

    # Render previous messages
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # Input box
    if question := st.chat_input("Ask a business question…"):
        # User message
        st.session_state.messages.append(
            {"role": "user", "content": question}
        )
        with st.chat_message("user"):
            st.markdown(question)

        # Assistant response
        with st.chat_message("assistant"):
            with st.spinner("Analyzing data..."):
                result = agent(question)

            render_result(result)

            # Store assistant message (summary later)
            st.session_state.messages.append(
                {
                    "role": "assistant",
                    "content": "Here are the results based on your question."
                }
            )