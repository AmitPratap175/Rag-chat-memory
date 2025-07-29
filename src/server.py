import json
import os
from fastapi import FastAPI, WebSocket, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from datetime import datetime
from .cust_logger import logger, set_files_message_color
import shutil
from .settings import settings
from pathlib import Path

from langchain_core.messages import AIMessageChunk, HumanMessage
from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver
from src.ai_companion.graph import graph_builder
from src.ai_companion.settings import settings as ai_settings

app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Set log message color for all logs from this file to 'purple' for easier identification in logs
set_files_message_color('purple')

# Mount static files directory from React frontend build.
# Enables serving CSS, JS, images etc. at /static path.
# app.mount("/static", StaticFiles(directory=Path(__file__).parent/"frontend/build/static"), name="static")

app.mount("/assets", StaticFiles(directory="frontend/dist/assets"), name="assets")

async def process_input(content: str, user_uuid: str):
    async with AsyncSqliteSaver.from_conn_string(ai_settings.SHORT_TERM_MEMORY_DB_PATH) as short_term_memory:
        graph = graph_builder.compile(checkpointer=short_term_memory)

        # Add new user message
        messages = [HumanMessage(content=content)]

        collected_chunks = ""
        async for chunk in graph.astream(
            {"messages": messages},
            {"configurable": {"thread_id": user_uuid}},
            stream_mode="messages",
        ):
            if chunk[1]["langgraph_node"] == "conversation_node" and isinstance(chunk[0], AIMessageChunk):
                collected_chunks += chunk[0].content

        output_state = await graph.aget_state(config={"configurable": {"thread_id": user_uuid}})
        return output_state, collected_chunks



@app.get("/")
async def serve_root():
    """
    Serve the root route "/".

    Returns:
    --------
    FileResponse
        Sends the React app's main index.html file to bootstrap the SPA frontend.
    """
    return FileResponse(Path(__file__).parent/os.path.join("frontend", "dist", "index.html"))

@app.get("/{full_path:path}")
async def serve_frontend(full_path: str):
 
    file_path = os.path.join("frontend", "dist", full_path)
    # Serve static asset if exists, else fallback to SPA entrypoint
    if os.path.exists(file_path):
        return FileResponse(file_path)
    return FileResponse(os.path.join("frontend", "dist", "index.html"))


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """
    WebSocket endpoint for real-time bidirectional communication with the frontend.

    Maintains the lifecycle of the WebSocket connection and handles incoming messages using UIController.

    Logs all received messages, errors, and connection events with timestamp and conversation UUID.

    Parameters:
    -----------
    websocket : WebSocket
        The active WebSocket connection instance.

    Operations:
    -----------
    - Accepts connection
    - Listens continuously for incoming JSON messages with at least "uuid" and "message" keys
    - On first message (init flag), logs initialization
    - For subsequent messages, forwards content and uuid to UIController to process and respond
    - Handles JSON decode errors and general exceptions with detailed logs
    - Ensures graceful connection closure and logs connection termination
    """
    await websocket.accept()  # Accept incoming WebSocket connection
    user_uuid = None  # Tracks the unique conversation identifier for logging context
    try:
        while True:
            data = await websocket.receive_text()  # Wait for next message from frontend client

            # Log the raw received message with timestamp and conversation UUID (can be None initially)
            logger.info(json.dumps({
                "timestamp": datetime.now().isoformat(),
                "uuid": user_uuid,
                "received": json.loads(data)
            }))

            try:
                payload = json.loads(data)  # Parse JSON payload from received text
                user_uuid = payload.get("uuid")  # Extract conversation UUID
                message = payload.get("message")  # Extract user message content
                init = payload.get("init", False)  # Flag indicating first/init message of conversation

                if init:
                    # Log initialization event on first message of a conversation
                    logger.info(json.dumps({
                        "timestamp": datetime.now().isoformat(),
                        "uuid": user_uuid,
                        "op": "Initializing ws with client."
                    }))
                else:
                    pass
                    # For non-init messages with content, invoke async processing logic in UIController
                    if message:
                        output_state, output_response = await process_input(message, user_uuid)
                        await websocket.send_text(json.dumps({"on_chat_model_stream": output_response}))
            except json.JSONDecodeError as e:
                # Log JSON parsing errors with context for easier debugging
                logger.error(json.dumps({
                    "timestamp": datetime.now().isoformat(),
                    "uuid": user_uuid,
                    "op": f"JSON encoding error - {e}"
                }))
    except Exception as e:
        # Log any unexpected exceptions for operational monitoring and incident response
        logger.error(json.dumps({
            "timestamp": datetime.now().isoformat(),
            "uuid": user_uuid,
            "op": f"Error: {e}"
        }))
    finally:
        # On exit/close, log the connection termination event if UUID is known
        if user_uuid:
            logger.info(json.dumps({
                "timestamp": datetime.now().isoformat(),
                "uuid": user_uuid,
                "op": "Closing connection."
            }))
        try:
            # Attempt to close the WebSocket connection gracefully
            await websocket.close()
        except RuntimeError as e:
            # Catch specific error when connection was already closed by client
            logger.error(json.dumps({
                "timestamp": datetime.now().isoformat(),
                "uuid": user_uuid,
                "op": f"WebSocket close error: {e}"
            }))

@app.post("/api/upload-pdf")
async def upload_pdf(file: UploadFile = File(...)):
    file_location = Path(__file__).parent/os.path.join(settings.DATA_DIR, file.filename)
    with open(file_location, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    return {"message": f"File '{file.filename}' uploaded successfully!"}

# Entry point to run the FastAPI app when executing this file directly
# Uses uvicorn ASGI server with host 0.0.0.0 and port 8000, minimizing uvicorn default verbosity
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="warning")
