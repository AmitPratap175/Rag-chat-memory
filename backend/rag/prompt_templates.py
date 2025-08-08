from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

system_prompt = """You are a programming tutor grounded in the provided book excerpts;
explain step-by-step, ask quick checks, and move only when mastery is shown;
for code, provide best practices and small, runnable examples."""

qa_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", system_prompt),
        MessagesPlaceholder(variable_name="chat_history"),
        ("human", "{input}"),
    ]
)

code_critique_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", system_prompt),
        (
            "human",
            "I tried to solve this problem with the following code:\n\n```python\n{user_code}\n```\n\n"
            "But I got this error:\n\n```\n{error_traceback}\n```\n\n"
            "Based on the book, what did I do wrong? Give me a root-cause analysis, 3 concrete improvements, "
            "a corrected version, and a best-practice version.",
        ),
    ]
)

mastery_assessor_prompt = ChatPromptTemplate.from_messages(
