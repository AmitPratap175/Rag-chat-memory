import logging
from typing import List
from pathlib import Path
from datetime import datetime # New import

from src.chatbot.modules.memory.long_term.vector_store import get_vector_store
from src.settings import settings # Use main settings


class RAGManager:
    """Manages the Retrieval-Augmented Generation process."""

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.vector_store = get_vector_store()

    def get_relevant_documents(self, query: str) -> List[str]:
        """Retrieve relevant document chunks from the vector store."""
        document_filter = {"must": [{"key": "source", "match": {"value": "document"}}]}
        results = self.vector_store.search_memories(
            query, k=settings.RAG_TOP_K, filter=document_filter
        )
        self.logger.info(f"Retrieved {len(results)} document chunks for RAG.")
        return [memory.text for memory in results]

    def format_context(self, documents: List[str]) -> str:
        """Format the document chunks into a single context string."""
        return "\n\n---\n\n".join(documents)

    def add_documents(self, document_contents: List[str]):
        """Add document contents to the vector store."""
        self.logger.info(f"Adding {len(document_contents)} documents to vector store...")
        for content in document_contents:
            # Assuming content here is already cleaned text from files
            # Metadata can be enriched if needed, e.g., with filename, URL etc.
            metadata = {
                "source": "document",
                "timestamp": datetime.now().isoformat(),
            }
            self.vector_store.store_memory(text=content, metadata=metadata)
        self.logger.info("Documents added to vector store successfully.")


def get_rag_manager() -> RAGManager:
    """Get a RAGManager instance."""
    return RAGManager()