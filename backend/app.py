import os
import shutil
from fastapi import FastAPI, UploadFile, File, WebSocket, HTTPException
from pydantic import BaseModel
from typing import List
import uuid

from backend.ingestion.loader import Loader
from backend.ingestion.chunker import Chunker
from backend.ingestion.embedder import Embedder
from backend.ingestion.indexer import Indexer
from backend.rag.chain import chain as rag_chain
from backend.memory.chat_memory import ChatMemory
from backend.study.syllabus_builder import SyllabusBuilder
from backend.executor.sandbox import Sandbox
from backend.executor.tester import Tester
from backend.executor.comparer import Comparer

app = FastAPI()

class ChatMessage(BaseModel):
    session_id: str
    message: str

class CodeExecutionRequest(BaseModel):
    code: str
    tests: str

class StudyPlanRequest(BaseModel):
    book_id: str

@app.post("/api/upload")
async def upload_book(file: UploadFile = File(...)):
    book_id = str(uuid.uuid4())
    file_path = f"data/books/{book_id}_{file.filename}"
    os.makedirs(os.path.dirname(file_path), exist_ok=True)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Ingestion pipeline
    loader = Loader()
    documents = loader.load(file_path)
    chunker = Chunker()
    chunks = chunker.chunk(documents)
    embedder = Embedder()
    embeddings = embedder.embed(chunks)
    indexer = Indexer()
    indexer.index(chunks, embeddings, book_id)

    return {"message": "Book uploaded and indexed successfully.", "book_id": book_id}

@app.websocket("/api/chat")
async def chat(websocket: WebSocket):
    await websocket.accept()
    memory = ChatMemory().get_checkpointer()
    # This is a simplified chat flow for demonstration
    while True:
        data = await websocket.receive_json()
        message = ChatMessage(**data)
        async for event in rag_chain.astream(
            {"messages": [("human", message.message)]},
            config={"configurable": {"thread_id": message.session_id}, "checkpointer": memory},
        ):
            if "messages" in event:
                await websocket.send_json({"message": event["messages"][-1].content})

@app.post("/api/study/plan")
async def get_study_plan(request: StudyPlanRequest):
    # This is a placeholder for generating a study plan from an indexed book
    # A real implementation would fetch the book's text from the indexer or a storage
    # and then use the SyllabusBuilder.
    return {"message": "Study plan generation not fully implemented yet."}

@app.post("/api/execute")
async def execute_code(request: CodeExecutionRequest):
    tester = Tester()
    passed, output = tester.run_tests(request.code, request.tests)
