import re
from src.chatbot.graph.state import AICompanionState
from langchain_core.messages import AIMessage

from crawl4ai import WebCrawler

def url_check_node(state: AICompanionState):
    """
    Checks if the user's message is a URL.
    """
    user_message = state["messages"][-1].content
    url_pattern = re.compile(r'https?://\S+')
    is_url = bool(url_pattern.match(user_message))

    if is_url:
        return {"url_to_crawl": user_message}
    else:
        return {"url_to_crawl": None}

from src.quiz.generator import generate_questions_for_passage
from src.quiz.models import Passage
from src.quiz.database import SessionLocal

async def crawl_node(state: AICompanionState, config):
    """
    Crawls the URL and stores the content in the state.
    """
    url = state.get("url_to_crawl")
    if not url:
        return {}

    websocket = config["configurable"]["websocket"]
    await websocket.send_json({"event": "crawling"})

    crawler = WebCrawler()
    result = await crawler.run_async(url)

    if result:
        return {"crawled_content": result[0].text}
    else:
        return {"crawled_content": None}

import base64

async def file_upload_node(state: AICompanionState, config):
    """
    Handles file uploads.
    """
    user_message = state["messages"][-1].content

    # Simple check to see if the message is a base64 encoded file
    if ";base64," in user_message:
        websocket = config["configurable"]["websocket"]
        await websocket.send_json({"event": "crawling"})
        header, encoded = user_message.split(",", 1)
        decoded = base64.b64decode(encoded).decode("utf-8")
        return {"uploaded_file_content": decoded}
    else:
        return {"uploaded_file_content": None}

from src.chatbot.modules.rag.rag_manager import get_rag_manager

async def store_in_long_term_memory_node(state: AICompanionState):
    """
    Stores the content in the long-term memory.
    """
    content = state.get("crawled_content") or state.get("uploaded_file_content")
    if not content:
        return {}

    rag_manager = get_rag_manager()
    await rag_manager.add_documents([content])

    return {}

async def question_generation_node(state: AICompanionState, config):
    """
    Generates questions from the crawled content.
    """
    content = state.get("crawled_content") or state.get("uploaded_file_content")
    if not content:
        return {}

    db = SessionLocal()
    passages = []
    paragraphs = content.split('\n\n')
    for i, para in enumerate(paragraphs):
        if len(para.strip()) > 100:
            passage = Passage(
                passage_text=para.strip(),
                language="en"
            )
            db.add(passage)
            db.commit()
            db.refresh(passage)
            generate_questions_for_passage(passage)
            passages.append(passage)

    db.close()

    websocket = config["configurable"]["websocket"]
    await websocket.send_json({"event": "questions_ready", "payload": {"message": "I have generated some questions from the URL you provided. You can now start a quiz to test your knowledge."}})

    return {}
