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

async def question_generation_node(state: AICompanionState, config):
    """
    Generates questions from the crawled content.
    """
    content = state.get("crawled_content")
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
