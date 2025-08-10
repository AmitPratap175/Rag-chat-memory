import json
from langchain_core.prompts import ChatPromptTemplate
from src.chatbot.graph.utils.helpers import get_chat_model
from . import models, schemas
from .database import SessionLocal
from .prompts import QUESTION_GENERATION_PROMPT
import uuid

def generate_questions_for_passage(passage: models.Passage):

    prompt = ChatPromptTemplate.from_template(QUESTION_GENERATION_PROMPT)
    model = get_chat_model()

    chain = prompt | model

    response = chain.invoke({
        "passage_text": passage.passage_text,
    })

    try:
        # The response content is a JSON string, so we parse it
        question_data = json.loads(response.content)

        db = SessionLocal()
        for q in question_data.get("questions", []):
            # Add a UUID to each question
            q['id'] = str(uuid.uuid4())
            question = models.Question(
                passage_id=passage.id,
                type=q.get("type"),
                json_payload=q,
                difficulty=q.get("difficulty"),
            )
            db.add(question)
        db.commit()
        db.close()

        return {"message": "Questions generated successfully"}
    except json.JSONDecodeError:
        return {"error": "Failed to decode JSON from LLM response"}
