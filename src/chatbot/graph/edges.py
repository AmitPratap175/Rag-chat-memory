import re
from langgraph.graph import END
from typing_extensions import Literal

from src.chatbot.graph.state import AICompanionState
from src.chatbot.settings import settings


def should_summarize_conversation(
    state: AICompanionState,
) -> Literal["summarize_conversation_node", "__end__"]:
    messages = state["messages"]

    if len(messages) > settings.TOTAL_MESSAGES_SUMMARY_TRIGGER:
        return "summarize_conversation_node"

    return END


def route_to_rag(
    state: AICompanionState,
) -> Literal["rag_node", "conversation_node"]:
    """
    Routes to the RAG node if RAG is needed, otherwise to the conversation node.
    """
    print("---ROUTING TO RAG---")
    if state.get("requires_rag"):
        return "rag_node"
    return "conversation_node"


def route_to_input_handler(state: AICompanionState):
    """
    Routes to the correct input handler based on the user's message.
    """
    user_message = state["messages"][-1].content
    if ";base64," in user_message:
        return "file_upload_node"
    elif re.match(r'https?://\S+', user_message):
        return "url_check_node"
    else:
        return "initial_check_node"


def evaluate_answer(
    state: AICompanionState,
) -> Literal["rewrite_query_node", "conversation_node"]:
    """
    Evaluates the candidate answer and routes to the rewrite_query_node if the answer needs refinement,
    otherwise to the conversation_node.
    """
    print("---EVALUATING ANSWER---")
    if state.get("is_sufficient"):
        return "conversation_node"
    return "rewrite_query_node"
