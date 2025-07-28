import streamlit as st
import sys
import os

# Add the project root directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')))

from io import BytesIO

from langchain_core.messages import AIMessageChunk, HumanMessage
from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver

from ai_companion.graph import graph_builder
from ai_companion.modules.image import ImageToText
from ai_companion.modules.speech import SpeechToText, TextToSpeech
from ai_companion.settings import settings
import wave
import asyncio

# Initialize module instances
speech_to_text = SpeechToText()
text_to_speech = TextToSpeech()
image_to_text = ImageToText()

# Set thread_id in session
if "thread_id" not in st.session_state:
    st.session_state.thread_id = 1

st.title("🧠 AI Companion")

# Text or image input
st.subheader("💬 Chat")
text_input = st.text_area("Type your message here", "")
image_file = st.file_uploader("Upload an image", type=["jpg", "jpeg", "png"])

# Audio input
st.subheader("🎤 Audio")
audio_file = st.file_uploader("Upload an audio file", type=["mp3", "wav", "mpeg"])

def pcm_to_wav_bytes(pcm: bytes, channels: int = 1, rate: int = 24000, sample_width: int = 2) -> BytesIO:
    """
    Convert PCM byte data to WAV format in-memory.

    Returns:
        BytesIO: A file-like object containing the WAV audio.
    """
    buffer = BytesIO()
    with wave.open(buffer, 'wb') as wf:
        wf.setnchannels(channels)
        wf.setsampwidth(sample_width)
        wf.setframerate(rate)
        wf.writeframes(pcm)
    buffer.seek(0)  # Important!
    return buffer

async def process_input(content: str):
    async with AsyncSqliteSaver.from_conn_string(settings.SHORT_TERM_MEMORY_DB_PATH) as short_term_memory:
        graph = graph_builder.compile(checkpointer=short_term_memory)
        msg = HumanMessage(content=content)

        collected_chunks = ""
        async for chunk in graph.astream(
            {"messages": [msg]},
            {"configurable": {"thread_id": st.session_state.thread_id}},
            stream_mode="messages",
        ):
            if chunk[1]["langgraph_node"] == "conversation_node" and isinstance(chunk[0], AIMessageChunk):
                collected_chunks += chunk[0].content

        output_state = await graph.aget_state(config={"configurable": {"thread_id": st.session_state.thread_id}})
        return output_state, collected_chunks

def play_audio_buffer(buffer: bytes, label="AI Audio Response"):
    st.audio(buffer, format="audio/mp3")

async def main():
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

        with st.spinner("Thinking..."):
            output_state, ai_response = await process_input(content)

        st.markdown(f"**AI:** {ai_response}")

        if output_state.values.get("workflow") == "audio":
            audio_buffer = output_state.values["audio_buffer"]
            play_audio_buffer(pcm_to_wav_bytes(audio_buffer))

        elif output_state.values.get("workflow") == "image":
            image_path = output_state.values["image_path"]
            st.image(image_path)

    if audio_file:
        st.subheader("📝 Audio Transcription & Response")
        if st.button("Transcribe and Respond"):
            with st.spinner("Processing audio..."):
                audio_data = audio_file.read()
                transcription = await speech_to_text.transcribe(audio_data)
                st.markdown(f"**You (transcribed):** {transcription}")

                output_state, output_response = await process_input(transcription)

                # print("--------------------->",type(output_state), output_state.keys() if hasattr(output_state, "keys") else dir(output_state))

                # response = BytesIO(output_response)
                print(f"AI Response: {output_response}")

                # Synthesize response to audio
                audio_buffer = await text_to_speech.synthesize(output_response)

                st.markdown(f"**AI:** {output_response}")
                play_audio_buffer(pcm_to_wav_bytes(audio_buffer))

# Run async event loop
if __name__ == "__main__":
    asyncio.run(main())
