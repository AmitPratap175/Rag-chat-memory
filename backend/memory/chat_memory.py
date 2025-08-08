from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver
import os

class ChatMemory:
    def __init__(self, db_path="data/memory/chat_memory.db"):
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self.memory = AsyncSqliteSaver.from_conn_string(db_path)

    def get_checkpointer(self):
        return self.memory
