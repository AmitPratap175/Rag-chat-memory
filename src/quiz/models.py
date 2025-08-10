from sqlalchemy import Column, Integer, String, JSON, DateTime, Boolean, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .database import Base

class Scrape(Base):
    __tablename__ = "scrapes"

    id = Column(Integer, primary_key=True, index=True)
    url = Column(String, unique=True, index=True)
    html = Column(Text)
    text = Column(Text)
    meta = Column(JSON)
    status = Column(String, default="pending")
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    passages = relationship("Passage", back_populates="scrape")

class Passage(Base):
    __tablename__ = "passages"

    id = Column(Integer, primary_key=True, index=True)
    scrape_id = Column(Integer, ForeignKey("scrapes.id"))
    passage_text = Column(Text)
    start_offset = Column(Integer)
    end_offset = Column(Integer)
    language = Column(String)
    topics = Column(JSON)

    scrape = relationship("Scrape", back_populates="passages")
    questions = relationship("Question", back_populates="passage")

class Question(Base):
    __tablename__ = "questions"

    id = Column(Integer, primary_key=True, index=True)
    passage_id = Column(Integer, ForeignKey("passages.id"))
    type = Column(String)
    json_payload = Column(JSON)
    difficulty = Column(Integer)
    created_by = Column(String, default="auto")
    curated = Column(Boolean, default=False)
    curated_by = Column(String, nullable=True)
    curated_at = Column(DateTime(timezone=True), nullable=True)

    passage = relationship("Passage", back_populates="questions")
