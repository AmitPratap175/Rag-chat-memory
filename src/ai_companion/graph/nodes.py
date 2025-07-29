from langchain_core.messages import AIMessage, HumanMessage, RemoveMessage
from langchain_core.runnables import RunnableConfig

from ai_companion.graph.state import AICompanionState
from ai_companion.graph.utils.chains import (
    get_character_response_chain,
    get_rag_router_chain,
    get_rag_chain,
    get_answer_evaluator_chain,
)
from ai_companion.graph.utils.helpers import (
    get_chat_model,
)
from ai_companion.modules.memory.long_term.memory_manager import get_memory_manager
from ai_companion.modules.rag.rag_manager import get_rag_manager
from ai_companion.modules.schedules.context_generation import ScheduleContextGenerator
from ai_companion.settings import settings


def context_injection_node(state: AICompanionState):
    schedule_context = ScheduleContextGenerator.get_current_activity()
    if schedule_context != state.get("current_activity", ""):
        apply_activity = True
    else:
        apply_activity = False
    return {"apply_activity": apply_activity, "current_activity": schedule_context}


async def conversation_node(state: AICompanionState, config: RunnableConfig):
    current_activity = ScheduleContextGenerator.get_current_activity()
    memory_context = state.get("memory_context", "")

    chain = get_character_response_chain(state.get("summary", ""))

    response = await chain.ainvoke(
        {
            "messages": state["messages"],
            "current_activity": current_activity,
            "memory_context": memory_context,
        },
        config,
    )
    return {"messages": AIMessage(content=response)}


async def summarize_conversation_node(state: AICompanionState):
    model = get_chat_model()
    summary = state.get("summary", "")

    if summary:
        summary_message = (
            f"This is summary of the conversation to date between Ava and the user: {summary}\n\n"
            "Extend the summary by taking into account the new messages above:"
        )
    else:
        summary_message = (
            "Create a summary of the conversation above between Ava and the user. "
            "The summary must be a short description of the conversation so far, "
            "but that captures all the relevant information shared between Ava and the user:"
        )

    messages = state["messages"] + [HumanMessage(content=summary_message)]
    response = await model.ainvoke(messages)

    delete_messages = [RemoveMessage(id=m.id) for m in state["messages"][: -settings.TOTAL_MESSAGES_AFTER_SUMMARY]]
    return {"summary": response.content, "messages": delete_messages}


async def memory_extraction_node(state: AICompanionState):
    """Extract and store important information from the last turn of the conversation."""
    if not state["messages"] or len(state["messages"]) < 2:
        return {}

    memory_manager = get_memory_manager()
    # The last two messages are the user's query and the AI's response
    last_turn_messages = state["messages"][-2:]
    conversation_to_memorize = "\n".join(
        [f"{m.type}: {m.content}" for m in last_turn_messages]
    )
    await memory_manager.extract_and_store_memories(
        HumanMessage(content=conversation_to_memorize)
    )
    return {}


def memory_injection_node(state: AICompanionState):
    """Retrieve and inject relevant memories into the character card."""
    memory_manager = get_memory_manager()

    # Get relevant memories based on recent conversation
    recent_context = " ".join([m.content for m in state["messages"][-3:]])
    memories = memory_manager.get_relevant_memories(recent_context)

    # Format memories for the character card
    memory_context = memory_manager.format_memories_for_prompt(memories)

    return {"memory_context": memory_context}


# RAG-related nodes
async def initial_check_node(state: AICompanionState):
    """
    Determines if RAG is needed to answer the user's query.
    """
    print("---INITIAL CHECK---")
    rag_router_chain = get_rag_router_chain()
    response = await rag_router_chain.ainvoke({"messages": state["messages"][-1:]})
    return {"requires_rag": response.requires_rag}


async def rag_node(state: AICompanionState):
    """
    Retrieves relevant documents from the vector store.
    """
    print("---RAG NODE---")
    rag_manager = get_rag_manager()
    query = state["messages"][-1].content
    documents = rag_manager.get_relevant_documents(query)
    return {"rag_context": documents}


async def generate_candidate_answer_node(state: AICompanionState):
    """
    Generates a candidate answer using the retrieved documents.
    """
    print("---GENERATE CANDIDATE ANSWER---")
    rag_chain = get_rag_chain()
    rag_context = "\n\n---\n\n".join(state["rag_context"])
    response = await rag_chain.ainvoke(
        {"context": rag_context, "question": state["messages"][-1].content}
    )
    return {"candidate_answer": response}


async def evaluate_answer_node(state: AICompanionState):
    """
    Evaluates the candidate answer and decides on the next step.
    """
    print("---EVALUATE ANSWER---")
    evaluator_chain = get_answer_evaluator_chain()
    rag_context = "\n\n---\n\n".join(state["rag_context"])
    response = await evaluator_chain.ainvoke(
        {
            "context": rag_context,
            "question": state["messages"][-1].content,
            "answer": state["candidate_answer"],
        }
    )
    return {
        "is_sufficient": response.is_sufficient,
        "corrected_query": response.corrected_query,
    }


async def rewrite_query_node(state: AICompanionState):
    """
    Rewrites the user's query for better retrieval results.
    """
    print("---REWRITE QUERY---")
    # For now, we'll just use the corrected query from the evaluator
    return {"messages": [HumanMessage(content=state["corrected_query"])]}
