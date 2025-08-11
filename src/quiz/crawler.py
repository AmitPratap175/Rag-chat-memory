import asyncio
import os
import hashlib
import regex as re
from urllib.parse import urldefrag, urlparse
from typing import List

from crawl4ai import (
    AsyncWebCrawler,
    BrowserConfig,
    CrawlerRunConfig,
    CacheMode,
    MemoryAdaptiveDispatcher
)
from src.settings import settings
from src.ingestion.markdown_cleaner import MarkdownCleaner # New import
from src.chatbot.modules.memory.long_term.vector_store import get_vector_store # New import
import uuid # New import
from datetime import datetime # Fix: import datetime

from . import schemas # Keep schemas for CrawlRequest
from .generator import generate_questions_for_passage # Will modify this function

def url_to_filename(url: str, default="page", ext=".md") -> str:
    parsed = urlparse(url)
    path = parsed.path.strip("/")

    if path:
        base = path.split("/")[-1]
    else:
        base = parsed.netloc.replace(".", "_")

    base = re.sub(r"\W+", "_", base).strip("_")

    if not base:
        base = hashlib.md5(url.encode()).hexdigest()

    return f"{base}{ext}"

def normalize_url(url):
    return urldefrag(url)[0]


async def crawl_urls(crawl_request: schemas.CrawlRequest):
    browser_config = BrowserConfig(headless=True, verbose=False)
    run_config = CrawlerRunConfig(
        cache_mode=CacheMode.BYPASS,
        stream=False
    )
    dispatcher = MemoryAdaptiveDispatcher(
        memory_threshold_percent=70.0,
        check_interval=1.0,
        max_session_permit=10
    )

    scraped_dir = settings.SCRAPED_DIR
    documents_dir = settings.DOCUMENTS_DIR
    os.makedirs(scraped_dir, exist_ok=True)
    os.makedirs(documents_dir, exist_ok=True)

    cleaner = MarkdownCleaner()
    vector_store = get_vector_store()
    all_processed_contents = []

    async with AsyncWebCrawler(config=browser_config) as crawler:
        if crawl_request.crawl_mode == "single":
            for url in crawl_request.urls:
                result = await crawler.arun(url=url, config=run_config)
                if result and result.success:
                    markdown = result.markdown or ""
                    safe_filename_raw = url_to_filename(result.url, ext=".md")
                    cleaned_text = await cleaner.process_files(markdown, safe_filename_raw)
                    all_processed_contents.append((cleaned_text, result.url)) # Store cleaned text and original URL
                    print(f"[INFO] Processed {cleaned_text}")

                    # Save raw markdown to scraped_dir (optional, for debugging/archiving)
                    file_path_raw = os.path.join(scraped_dir, safe_filename_raw)
                    with open(file_path_raw, "w", encoding="utf-8") as f:
                        f.write(markdown)

                    # Save cleaned markdown to documents_dir
                    # safe_filename_cleaned = url_to_filename(result.url, ext="_cleaned.md")
                    # file_path_cleaned = os.path.join(documents_dir, safe_filename_cleaned)
                    # with open(file_path_cleaned, "w", encoding="utf-8") as f:
                    #     f.write(cleaned_text)

                    # Store cleaned content in Qdrant
                    metadata = {
                        "id": str(uuid.uuid4()),
                        "source": result.url,
                        "document_name": safe_filename_raw,
                        "timestamp": datetime.now().isoformat() # Add datetime import if needed
                    }
                    vector_store.store_memory(text=cleaned_text, metadata=metadata)

                else:
                    print(f"[ERROR] {url}: {result.error_message if result else 'Unknown error'}")
        else: # Default to recursive
            visited = set()
            current_urls = set([normalize_url(u) for u in crawl_request.urls])

            for depth in range(3):  # Max depth of 3 for recursive crawling
                urls_to_crawl = [normalize_url(url) for url in current_urls if normalize_url(url) not in visited]

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
                        cleaned_text = await cleaner.clean_text(markdown)
                        all_processed_contents.append((cleaned_text, result.url)) # Store cleaned text and original URL

                        # Save raw markdown to scraped_dir (optional)
                        safe_filename_raw = url_to_filename(result.url, ext=".md")
                        file_path_raw = os.path.join(scraped_dir, safe_filename_raw)
                        with open(file_path_raw, "w", encoding="utf-8") as f:
                            f.write(markdown)

                        # Save cleaned markdown to documents_dir
                        safe_filename_cleaned = url_to_filename(result.url, ext="_cleaned.md")
                        file_path_cleaned = os.path.join(documents_dir, safe_filename_cleaned)
                        with open(file_path_cleaned, "w", encoding="utf-8") as f:
                            f.write(cleaned_text)

                        # Store cleaned content in Qdrant
                        metadata = {
                            "id": str(uuid.uuid4()),
                            "source": result.url,
                            "document_name": safe_filename_cleaned,
                            "timestamp": datetime.now().isoformat() # Add datetime import if needed
                        }
                        vector_store.store_memory(text=cleaned_text, metadata=metadata)

                        for link in result.links.get("internal", []):
                            next_url = normalize_url(link["href"])
                            if next_url not in visited:
                                next_level_urls.add(next_url)
                    else:
                        print(f"[ERROR] {result.url}: {result.error_message}")

                current_urls = next_level_urls

    # Generate questions from all processed (cleaned) contents
    for cleaned_text, original_url in all_processed_contents:
        generate_questions_for_passage(cleaned_text, original_url)

    return {"message": "Crawling, cleaning, Qdrant ingestion, and question generation completed successfully"}