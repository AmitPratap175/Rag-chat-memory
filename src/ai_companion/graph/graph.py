from functools import lru_cache

from langgraph.graph import END, START, StateGraph

from ai_companion.graph.edges import (
    should_summarize_conversation,
    route_to_rag,
    evaluate_answer,
)
from ai_companion.graph.nodes import (
    context_injection_node,
    conversation_node,
    memory_extraction_node,
    memory_injection_node,
    summarize_conversation_node,
    initial_check_node,
    rag_node,
    generate_candidate_answer_node,
    evaluate_answer_node,
    rewrite_query_node,
)
from ai_companion.graph.state import AICompanionState


@lru_cache(maxsize=1)
def create_workflow_graph():
    graph_builder = StateGraph(AICompanionState)

    # Add all nodes
    graph_builder.add_node("memory_extraction_node", memory_extraction_node)
    graph_builder.add_node("context_injection_node", context_injection_node)
    graph_builder.add_node("memory_injection_node", memory_injection_node)
    graph_builder.add_node("summarize_conversation_node", summarize_conversation_node)
    graph_builder.add_node("initial_check_node", initial_check_node)
    graph_builder.add_node("rag_node", rag_node)
    graph_builder.add_node("generate_candidate_answer_node", generate_candidate_answer_node)
    graph_builder.add_node("evaluate_answer_node", evaluate_answer_node)
    graph_builder.add_node("rewrite_query_node", rewrite_query_node)
    graph_builder.add_node("conversation_node", conversation_node)


    # Define the flow
    graph_builder.add_edge(START, "context_injection_node")
    graph_builder.add_edge("context_injection_node", "memory_injection_node")
    graph_builder.add_edge("memory_injection_node", "initial_check_node")

    # RAG loop
    graph_builder.add_conditional_edges("initial_check_node", route_to_rag)
    graph_builder.add_edge("rag_node", "generate_candidate_answer_node")
    graph_builder.add_edge("generate_candidate_answer_node", "evaluate_answer_node")
    graph_builder.add_conditional_edges("evaluate_answer_node", evaluate_answer)
    graph_builder.add_edge("rewrite_query_node", "rag_node")

    # Final response
    graph_builder.add_edge("conversation_node", "memory_extraction_node")
    graph_builder.add_conditional_edges(
        "memory_extraction_node", should_summarize_conversation
    )
    graph_builder.add_edge("summarize_conversation_node", END)

    return graph_builder


# Compiled without a checkpointer. Used for LangGraph Studio
graph = create_workflow_graph().compile()
