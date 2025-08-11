import re
import os
import hashlib
from urllib.parse import urldefrag, urlparse

from src.chatbot.graph.state import AICompanionState
from langchain_core.messages import AIMessage

from crawl4ai import (
    AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, CacheMode,
    MemoryAdaptiveDispatcher
)
from src.settings import settings # Import settings to get DATA_DIR
# from src.ingest_documents import main as ingest_main # No longer needed

def url_to_filename(url: str, default="page", ext=".md") -> str:
    parsed = urlparse(url)
    path = parsed.path.strip("/")

    # Use last part of path, or domain if path is empty
    if path:
        base = path.split("/")[-1]
    else:
        base = parsed.netloc.replace(".", "_")

    # Replace non-word characters with underscores
    base = re.sub(r"\W+", "_", base).strip("_")

    # Fallback to hash if empty
    if not base:
        base = hashlib.md5(url.encode()).hexdigest()

    return f"{base}{ext}"

def normalize_url(url):
    return urldefrag(url)[0]  # Remove fragment (part after #)


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

# from src.quiz.generator import generate_questions_for_passage # No longer needed here
# from src.quiz.models import Passage # No longer needed here
# from src.quiz.database import SessionLocal # No longer needed here

async def crawl_node(state: AICompanionState, config):
    """
    Crawls the URL and stores the content in the state.
    """
    url = state.get("url_to_crawl")
    if not url:
        return {}

    websocket = config["configurable"]["websocket"]
    await websocket.send_json({"event": "crawling"})

    browser_config = BrowserConfig(headless=True, verbose=False)
    run_config = CrawlerRunConfig(
        cache_mode=CacheMode.BYPASS,
        stream=False
    )
    dispatcher = MemoryAdaptiveDispatcher(
        memory_threshold_percent=70.0,
        check_interval=1.0,
        max_session_permit=10  # Max concurrent browser sessions
    )

    visited = set()
    current_urls = set([normalize_url(url)])
    raw_scraped_file_paths = [] # To store paths of raw markdown files

    # Ensure scraped_dir exists
    scraped_dir = settings.SCRAPED_DIR
    os.makedirs(scraped_dir, exist_ok=True)

    async with AsyncWebCrawler(config=browser_config) as crawler:
        for depth in range(3):  # Max depth of 3 for recursive crawling
            urls_to_crawl = [normalize_url(u) for u in current_urls if normalize_url(u) not in visited]

            if not urls_to_crawl:
                break

            results = await crawler.arun_many(
                urls=urls_to_crawl,
                config=run_config,
                dispatcher=dispatcher
            )

            next_level_urls = set()

            for result in results:
                norm_url = normalize_url(result.url)
                visited.add(norm_url)

                if result.success:
                    markdown = result.markdown or ""
                    
                    # Save raw markdown to file
                    safe_filename = url_to_filename(result.url)
                    file_path = os.path.join(scraped_dir, safe_filename)
                    with open(file_path, "w", encoding="utf-8") as f:
                        f.write(markdown)
                    raw_scraped_file_paths.append(file_path) # Collect path

                    # Collect new internal links
                    for link in result.links.get("internal", []):
                        next_url = normalize_url(link["href"])
                        if next_url not in visited:
                            next_level_urls.add(next_url)
                else:
                    print(f"[ERROR] {result.url}: {result.error_message}")

            current_urls = next_level_urls

    return {"raw_scraped_file_paths": raw_scraped_file_paths}

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

# from src.chatbot.modules.rag.rag_manager import get_rag_manager # No longer needed here
# from src.ingestion.markdown_cleaner import MarkdownCleaner # No longer needed here

async def store_in_long_term_memory_node(state: AICompanionState):
    """
    This node is now a no-op as cleaning and ingestion are handled by crawler.py.
    """
    return {}

async def question_generation_node(state: AICompanionState, config):
    """
    This node is now a no-op as question generation is handled by crawler.py.
    """
    websocket = config["configurable"]["websocket"]
    await websocket.send_json({"event": "questions_ready", "payload": {"message": "I have generated some questions from the URL you provided. You can now start a quiz to test your knowledge."}})
    return {}