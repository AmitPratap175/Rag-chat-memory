import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.pydantic_v1 import BaseModel, Field
from typing import List

class SyllabusTopic(BaseModel):
    topic_name: str = Field(description="The name of the topic or chapter.")
    subtopics: List[str] = Field(description="A list of subtopics or sections within this topic.")
    learning_objectives: List[str] = Field(description="A list of learning objectives for this topic.")

class Syllabus(BaseModel):
    book_title: str = Field(description="The title of the book.")
    topics: List[SyllabusTopic] = Field(description="The list of topics that make up the syllabus.")

SYLLABUS_GENERATION_PROMPT = ChatPromptTemplate.from_template(
    """You are an expert in instructional design. Based on the following table of contents or introductory text from a programming book, please generate a structured study plan (syllabus).

Extract the main topics, subtopics, and create a few learning objectives for each main topic.

Book Text:
---
{book_text}
---

Please provide the output in the requested JSON format.
"""
)

class SyllabusBuilder:
    def __init__(self):
