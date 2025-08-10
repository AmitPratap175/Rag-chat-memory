from pydantic import BaseModel
from typing import List, Optional

class CrawlRequest(BaseModel):
    urls: List[str]
    scrape_profile: Optional[dict] = None
    priority: Optional[int] = 0
    tag: Optional[str] = None
    run_now: Optional[bool] = False

class Quiz(BaseModel):
    id: int
    questions: List[int]

class QuizQuestion(BaseModel):
    id: int
    passage_id: int
    type: str
    json_payload: dict
    difficulty: int

class QuizAnswer(BaseModel):
    question_id: int
    answer: str
