import json
import os
from fastapi import FastAPI, WebSocket, UploadFile, File
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from datetime import datetime
from .cust_logger import logger, set_files_message_color
import shutil
from .settings import settings
from pathlib import Path

from langchain_core.messages import AIMessageChunk, HumanMessage
from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver
from src.chatbot.graph import graph_builder
from src.chatbot.settings import settings as ai_settings
from src.ingest_documents import main
from src.quiz import database as quiz_database

quiz_database.create_tables()

app = FastAPI()

# Set log message color for all logs from this file to 'purple' for easier identification in logs
set_files_message_color('purple')

# Mount static files directory from React frontend build.
# Enables serving CSS, JS, images etc. at /static path.
app.mount("/static", StaticFiles(directory=Path(__file__).parent/"frontend/build/static"), name="static")


async def process_input(content: str, user_uuid: str, websocket: WebSocket):
    async with AsyncSqliteSaver.from_conn_string(ai_settings.SHORT_TERM_MEMORY_DB_PATH) as short_term_memory:
        graph = graph_builder.compile(checkpointer=short_term_memory)

        # Add new user message
        messages = [HumanMessage(content=content)]

        collected_chunks = ""
        async for chunk in graph.astream(
            {"messages": messages},
            {"configurable": {"thread_id": user_uuid, "websocket": websocket}},
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
    return FileResponse(Path(__file__).parent/os.path.join("frontend", "build", "index.html"))

@app.get("/{full_path:path}")
async def serve_frontend(full_path: str):
    """
    Serve all other GET requests to enable React Router support for deep links.

    Parameters:
    -----------
    full_path : str
        The requested URI path after the root.

    Returns:
    --------
    FileResponse
        Returns the requested static file if it exists,
        otherwise falls back to sending index.html to let React Router handle routing.
    """
    file_path = Path(__file__).parent / os.path.join("frontend", "build", full_path)
    # Serve static asset if exists, else fallback to SPA entrypoint
    if os.path.exists(file_path):
        return FileResponse(file_path)
    return FileResponse(Path(__file__).parent / os.path.join("frontend", "build", "index.html"))

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
                        output_state, output_response = await process_input(message, user_uuid, websocket)
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

from src.quiz import crawler, schemas, crud
from src.quiz.database import SessionLocal, engine
from fastapi import Depends
from sqlalchemy.orm import Session

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/api/crawl")
async def crawl(crawl_request: schemas.CrawlRequest):
    return await crawler.crawl_urls(crawl_request)

@app.get("/api/stats")
async def get_stats(db: Session = Depends(get_db)):
    stats = crud.get_stats(db)
    return stats

@app.get("/api/questions")
async def get_questions(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    questions = crud.get_questions(db, skip=skip, limit=limit)
    return questions

@app.put("/api/questions/{question_id}")
async def update_question(question_id: int, updated_question: dict, db: Session = Depends(get_db)):
    question = crud.update_question(db, question_id=question_id, updated_question=updated_question)
    if question is None:
        return {"error": "Question not found"}
    return question

@app.delete("/api/questions/{question_id}")
async def delete_question(question_id: int, db: Session = Depends(get_db)):
    result = crud.delete_question(db, question_id=question_id)
    if result is None:
        return {"error": "Question not found"}
    return result

@app.get("/api/quiz/new")
async def new_quiz(limit: int = 10, db: Session = Depends(get_db)):
    questions = crud.get_random_questions(db, limit=limit)
    return questions

from src.quiz.quiz_handler import QuizManager

@app.post("/api/quiz/answer")
async def answer_quiz(answer: schemas.QuizAnswer, db: Session = Depends(get_db)):
    result = crud.check_answer(db, question_id=answer.question_id, answer=answer.answer)
    if result is None:
        return {"error": "Question not found"}
    return result

@app.websocket("/ws/quiz")
async def quiz_websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    quiz_manager = None
    try:
        while True:
            data = await websocket.receive_json()
            event = data.get("event")
            payload = data.get("payload")

            if event == "start_quiz":
                user_uuid = payload.get("uuid")
                quiz_manager = QuizManager(user_uuid)
                question = quiz_manager.start_quiz()
                await websocket.send_json({"event": "question", "payload": question.json_payload if question else None})

            elif event == "next_question":
                if quiz_manager:
                    question = quiz_manager.get_next_question()
                    if question:
                        await websocket.send_json({"event": "question", "payload": question.json_payload})
                    else:
                        await websocket.send_json({"event": "quiz_finished"})

            elif event == "answer":
                if quiz_manager:
                    question_id = payload.get("question_id")
                    answer = payload.get("answer")
                    result = quiz_manager.check_answer(question_id, answer)
                    await websocket.send_json({"event": "answer_result", "payload": result})

    except Exception as e:
        logger.error(f"Quiz WebSocket error: {e}")
    finally:
        if quiz_manager:
            quiz_manager.close()
        await websocket.close()

@app.post("/api/upload-pdf")
async def upload_pdf(file: UploadFile = File(...)):
    file_location = Path(__file__).parent/os.path.join(settings.DATA_DIR, file.filename)
    with open(file_location, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    await main()
    return {"message": f"File '{file.filename}' uploaded successfully!"}

# Entry point to run the FastAPI app when executing this file directly
# Uses uvicorn ASGI server with host 0.0.0.0 and port 8000, minimizing uvicorn default verbosity
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="warning")
