import streamlit as st
import sys
import os
import asyncio

# Add the project root directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')))

from langchain_core.messages import AIMessageChunk, HumanMessage
from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver

from ai_companion.graph import graph_builder
from ai_companion.modules.image import ImageToText
from ai_companion.modules.speech import SpeechToText, TextToSpeech
from ai_companion.settings import settings

# Initialize module instances
speech_to_text = SpeechToText()
text_to_speech = TextToSpeech()
image_to_text = ImageToText()

# Set initial state
if "thread_id" not in st.session_state:
    st.session_state.thread_id = 1

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []  # list of dicts with "role" and "content"

st.title("🧠 AI Companion - Conversational Mode")

# Text or image input
st.subheader("💬 Chat")
text_input = st.text_area("Type your message here", "")
image_file = st.file_uploader("Upload an image", type=["jpg", "jpeg", "png"])

# Audio input
st.subheader("🎤 Audio")
audio_file = st.file_uploader("Upload an audio file", type=["mp3", "wav", "mpeg"])

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

def play_audio_buffer(buffer: bytes, label="AI Audio Response"):
    st.audio(buffer, format="audio/mpeg3", start_time=0)

async def main():
    # Display chat history
    for msg in st.session_state.chat_history:
        role_label = "**You:**" if msg["role"] == "user" else "**AI:**"
        st.markdown(f"{role_label} {msg['content']}")

    # Process user message
    if st.button("Submit Text/Image"):
        content = text_input

        # Append image analysis if an image is uploaded
        if image_file:
            try:
                image_bytes = image_file.read()
                description = await image_to_text.analyze_image(
                    image_bytes,
                    "Please describe what you see in this image in the context of our conversation."
                )
                content += f"\n[Image Analysis: {description}]"
            except Exception as e:
                st.warning(f"Image analysis failed: {e}")

        if content.strip() == "":
            st.warning("Please enter a message or upload an image.")
            return

        st.session_state.chat_history.append({"role": "user", "content": content})

        with st.spinner("Thinking..."):
            output_state, ai_response = await process_input(content)

        st.session_state.chat_history.append({"role": "ai", "content": ai_response})
        st.rerun()

    # Audio processing
    if audio_file:
        st.subheader("📝 Audio Transcription & Response")
        if st.button("Transcribe and Respond"):
            with st.spinner("Processing audio..."):
                audio_data = audio_file.read()
                transcription = await speech_to_text.transcribe(audio_data)
                st.session_state.chat_history.append({"role": "user", "content": transcription})
                st.markdown(f"**You (transcribed):** {transcription}")

                output_state, response = await process_input(transcription)
                st.session_state.chat_history.append({"role": "ai", "content": response})

                audio_buffer = await text_to_speech.synthesize(response)
                play_audio_buffer(audio_buffer)
                st.rerun()

# Run async event loop
if __name__ == "__main__":
    asyncio.run(main())
