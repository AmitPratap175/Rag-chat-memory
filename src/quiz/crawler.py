from crawl4ai import WebCrawler
from . import models, schemas
from .database import SessionLocal

from .generator import generate_questions_for_passage

def create_passages(db, scrape):
    paragraphs = scrape.text.split('\n\n')
    for i, para in enumerate(paragraphs):
        if len(para.strip()) > 100: # Only consider paragraphs with more than 100 characters
            passage = models.Passage(
                scrape_id=scrape.id,
                passage_text=para.strip(),
                start_offset=scrape.text.find(para),
                end_offset=scrape.text.find(para) + len(para),
                language="en"
            )
            db.add(passage)
            db.commit()
            db.refresh(passage)
            generate_questions_for_passage(passage)

def crawl_urls(crawl_request: schemas.CrawlRequest):
    crawler = WebCrawler()
    results = crawler.run(urls=crawl_request.urls)

    db = SessionLocal()
    for result in results:
        scrape = models.Scrape(
            url=result.url,
            html=result.html,
            text=result.text,
            meta=result.metadata,
            status="completed"
        )
        db.add(scrape)
        db.commit()
        db.refresh(scrape)
        create_passages(db, scrape)

    db.close()

    return {"message": "Crawling and passage creation completed successfully"}
