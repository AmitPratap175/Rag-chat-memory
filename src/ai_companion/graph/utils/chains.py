from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from ai_companion.core.prompts import (
    CHARACTER_CARD_PROMPT,
    RAG_ROUTER_PROMPT,
    RAG_PROMPT,
    EVALUATE_ANSWER_PROMPT,
)
from ai_companion.graph.utils.helpers import AsteriskRemovalParser, get_chat_model
from ai_companion.graph.utils.schemas import RagRouter, AnswerEvaluator
from langchain_core.output_parsers import StrOutputParser


def get_rag_router_chain():
    model = get_chat_model(temperature=0.3).with_structured_output(RagRouter)

    prompt = ChatPromptTemplate.from_messages(
        [('system', RAG_ROUTER_PROMPT), MessagesPlaceholder(variable_name='messages')]
    )

    return prompt | model


def get_character_response_chain(summary: str = ''):
    model = get_chat_model()
    system_message = CHARACTER_CARD_PROMPT

    if summary:
        system_message += f'\n\nSummary of conversation earlier between Ava and the user: {summary}'

    prompt = ChatPromptTemplate.from_messages(
        [
            ('system', system_message),
            MessagesPlaceholder(variable_name='messages'),
        ]
    )

    return prompt | model | AsteriskRemovalParser()


def get_rag_chain():
    model = get_chat_model()

    prompt = ChatPromptTemplate.from_template(RAG_PROMPT)

    return prompt | model | StrOutputParser()


def get_answer_evaluator_chain():
    model = get_chat_model(temperature=0.3).with_structured_output(AnswerEvaluator)

    prompt = ChatPromptTemplate.from_template(EVALUATE_ANSWER_PROMPT)

    return prompt | model
