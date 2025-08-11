import json
from langchain_core.prompts import ChatPromptTemplate
from src.chatbot.graph.utils.helpers import get_chat_model
from .prompts import QUESTION_GENERATION_PROMPT
import uuid

def generate_questions_for_passage(passage_text: str, source_url: str = "unknown"):

    prompt = ChatPromptTemplate.from_template(QUESTION_GENERATION_PROMPT)
    model = get_chat_model()

    chain = prompt | model

    response = chain.invoke({
        "passage_text": passage_text,
        "source_url": source_url # Pass source URL to the prompt
    })

    try:
        # The response content is a JSON string, so we parse it
        question_data = json.loads(response.content)

        # Note: Questions are no longer stored in SQLite here.
        # If persistent storage for questions is needed, it should be handled elsewhere (e.g., Qdrant or another DB).

        return {"message": "Questions generated successfully"}
    except json.JSONDecodeError:
        return {"error": "Failed to decode JSON from LLM response"}
