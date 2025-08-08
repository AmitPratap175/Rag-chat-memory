from langgraph.graph import StateGraph, END, START
from typing import TypedDict, Annotated, List
from langchain_core.messages import AnyMessage
from .retriever import Retriever
from .prompt_templates import qa_prompt
from langchain_google_genai import ChatGoogleGenerativeAI
import os

class GraphState(TypedDict):
    messages: Annotated[List[AnyMessage], operator.add]

def retrieve(state):
    messages = state["messages"]
    retriever = Retriever()
    retrieved_docs = retriever.retrieve(messages[-1].content)
    context = "\n\n".join(retrieved_docs)
    return {"messages": state["messages"], "context": context}

def rag(state):
    context = state["context"]
    llm = ChatGoogleGenerativeAI(model="gemini/gemini-pro", google_api_key=os.environ["GOOGLE_API_KEY"])
    rag_chain = qa_prompt | llm
    response = rag_chain.invoke({"input": state["messages"][-1].content, "chat_history": state["messages"], "context": context})
    return {"messages": state["messages"] + [response]}

workflow = StateGraph(GraphState)
workflow.add_node("retrieve", retrieve)
workflow.add_node("rag", rag)
workflow.add_edge(START, "retrieve")
workflow.add_edge("retrieve", "rag")
workflow.add_edge("rag", END)
