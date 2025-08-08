import uuid
from typing import List

import chromadb
from langchain_core.documents import Document


class Indexer:
    def __init__(self, collection_name="books"):
        self.client = chromadb.Client()
        self.collection = self.client.get_or_create_collection(name=collection_name)

    def index_documents(self, chunks: List[Document], book_id: str):
        """Store document chunks in the vector store."""
        for i, chunk in enumerate(chunks):
            metadata = {
                "book_id": book_id,
                "chapter": chunk.metadata.get("chapter", "N/A"),
                "section": chunk.metadata.get("section", "N/A"),
                "page": chunk.metadata.get("page", -1),
                "chunk_index": i,
                "text": chunk.page_content,
            }
            self.collection.add(
                documents=[chunk.page_content], metadatas=[metadata], ids=[str(uuid.uuid4())]
            )
