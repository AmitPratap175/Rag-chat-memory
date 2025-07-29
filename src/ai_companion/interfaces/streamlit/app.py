# frontend/app.py

import streamlit as st
import base64
from io import StringIO
import uuid

import sys
import os
import asyncio

# Add the project root directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')))

from langchain_core.messages import AIMessageChunk, HumanMessage
from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver

from src.ai_companion.graph import graph_builder
from src.ai_companion.settings import settings


# * APP INPUTS ----

DB_OPTIONS = {
    "Northwind Database": "Northwind Database",  # Match backend name
}

MODEL_LIST = ["gemini-1.5-flash", "gemini-2.0-flash"]

FASTAPI_URL = "http://0.0.0.0:8000/query"

TITLE = "Conversational Agent with Memory"

# * STREAMLIT APP SETUP ----

st.set_page_config(page_title=TITLE, page_icon="📊")

st.markdown(
    """
    <style>
        /* Target only elements within the sidebar */
        [data-testid="stSidebar"] {
            background-color: #FFFFFF !important;
        }
        
        /* All text in sidebar */
        [data-testid="stSidebar"] * {
            color: #000000 !important;
        }
        
        /* Text input fields - crucial fix */
        [data-testid="stSidebar"] [data-testid="stTextInput"] input {
            color: #000000 !important;
            background-color: #FFFFFF !important;
        }
        
        /* Selectbox styling */
        [data-testid="stSidebar"] [data-testid="stSelectbox"] div {
            background-color: #FFFFFF !important;
        }
        
        /* Input field borders */
        [data-testid="stSidebar"] .stTextInput div div input:focus {
            border-color: #000000 !important;
            box-shadow: 0 0 0 0.2rem rgba(0,0,0,0.25) !important;
        }
        
        /* Placeholder text */
        [data-testid="stSidebar"] input::placeholder {
            color: #666666 !important;
            opacity: 1 !important;
        }
        
        /* Dropdown arrow */
        [data-testid="stSidebar"] [data-testid="stSelectbox"] svg {
            color: #000000 !important;
        }
        /* Target the container of the input and button */
[data-testid="stSidebar"] [data-testid="stTextInput"] div:has(> input[type="password"]) div {
    background-color: #FFFFFF !important;
    border-color: #000000 !important; /* If you want a border */
    display: flex !important; /* Enable Flexbox */
    align-items: center !important; /* Vertically align items */
    overflow: hidden !important; /* Clip any potential overflow */
}

/* Target the input element */
[data-testid="stSidebar"] [data-testid="stTextInput"] div:has(> input[type="password"]) input {
    flex-grow: 1 !important; /* Allow input to take up available space */
    padding-right: 0 !important; /* Ensure no right padding on input */
    margin-right: 0 !important; /* Ensure no right margin on input */
}

/* Target the button */
[data-testid="stSidebar"] [data-testid="stTextInput"] div:has(> input[type="password"]) button {
    background-color: #FFFFFF !important;
    padding: 0 !important;
    margin-left: auto !important; /* Push button to the right */
    border: none !important;
    border-radius: 0 !important;
    min-width: 0 !important; /* Prevent button from expanding */
}

.st-d6 {
            padding-right: 5px !important;
            color: white !important;
            background-color: white !important; /* Or target the parent */
        }
    button[aria-label="Show password text"] {
        padding-right: 14px !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)
st.title(TITLE)

st.markdown("""
Customer Support Agent with Memory
""")


# * STREAMLIT APP SIDEBAR ----

# Logo
file_path = "/home/dspratap/Documents/suneater175/whatsapp-bot-best/src/ai_companion/interfaces/img/normal_portrait.svg"
with open(file_path, "rb") as f:
    data = f.read()
encoded = base64.b64encode(data).decode()
logo_html = f"""
<div style="text-align: center; padding: 10px 0;">
    <img src="data:image/svg+xml;base64,{encoded}" width="100" />
</div>
"""
st.sidebar.markdown(logo_html, unsafe_allow_html=True)

# Sidebar Inputs
model_option = st.sidebar.selectbox("Choose Gemini model", MODEL_LIST, index=0)

# * CHAT INTERFACE ----

if "messages" not in st.session_state:
    st.session_state.messages = []

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []  # list of dicts with "role" and "content"

# TODO: Generate and store a single `thread_id` per session to ensure consistent session context with the backend.
# Previously, a new `thread_id` was generated for *every* user message, causing the backend to treat each message as a new, isolated thread.
# Now, we only create the thread ID once per user session and reuse it for every API call during that session.
if "thread_id" not in st.session_state:
    st.session_state.thread_id = str(uuid.uuid4())
    st.session_state.query_count = 0

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

async def process_input(content: str):
    async with AsyncSqliteSaver.from_conn_string(settings.SHORT_TERM_MEMORY_DB_PATH) as short_term_memory:
        graph = graph_builder.compile(checkpointer=short_term_memory)

        # Include full chat history
        messages = [HumanMessage(m["content"]) if m["role"] == "user" else AIMessageChunk(m["content"])
                    for m in st.session_state.chat_history]

        # Add new user message
        messages.append(HumanMessage(content=content))

        collected_chunks = ""
        async for chunk in graph.astream(
            {"messages": messages},
            {"configurable": {"thread_id": st.session_state.thread_id}},
            stream_mode="messages",
        ):
            if chunk[1]["langgraph_node"] == "conversation_node" and isinstance(chunk[0], AIMessageChunk):
                collected_chunks += chunk[0].content

        output_state = await graph.aget_state(config={"configurable": {"thread_id": st.session_state.thread_id}})
        return output_state, collected_chunks

question = st.chat_input("Enter your question here:", key="query_input")

async def main():
    if question:
        with st.spinner("Thinking..."):
            st.chat_message("user").markdown(question)
            st.session_state.messages.append({"role": "user", "content": question})

            try:
                output_state, ai_response = await process_input(question)

                st.session_state.messages.append({"role": "assistant", "content": ai_response})
                st.session_state.query_count += 1  # Increment query counter
                st.rerun()

            except Exception as e:
                st.error(f"Error occurred: {e}")
    # else:
    #     st.warning("Please enter a message.")
    #     return


# Run async event loop
if __name__ == "__main__":
    asyncio.run(main())

