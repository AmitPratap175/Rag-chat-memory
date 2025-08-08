import os
from langchain_google_genai import ChatGoogleGenerativeAI
from backend.rag.prompt_templates import code_critique_prompt


class Comparer:
    def __init__(self):
        if "GOOGLE_API_KEY" not in os.environ:
            raise ValueError("GOOGLE_API_KEY environment variable not set.")
        self.llm = ChatGoogleGenerativeAI(model="gemini/gemini-pro", temperature=0)

    def compare_and_suggest(self, user_code: str, error_traceback: str):
        """Compares user code with a reference and provides suggestions."""
        chain = code_critique_prompt | self.llm
        response = chain.invoke(
            {"user_code": user_code, "error_traceback": error_traceback}
        )
        return response.content


