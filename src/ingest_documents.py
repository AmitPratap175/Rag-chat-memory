import asyncio
import logging
import os
import sys
from pathlib import Path
from typing import List
import uuid

from src.chatbot.modules.memory.long_term.vector_store import get_vector_store
from langchain_community.document_loaders import (
    PyPDFLoader,
    UnstructuredMarkdownLoader,
)
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Supported file loaders
FILE_LOADERS = {
    ".pdf": PyPDFLoader,
    ".md": UnstructuredMarkdownLoader,
}


def load_documents(data_dir: Path) -> List[Document]:
    """Load all supported documents from the data directory."""
    documents = []
    for file_path in data_dir.iterdir():
        if file_path.suffix in FILE_LOADERS:
            loader_class = FILE_LOADERS[file_path.suffix]
            loader = loader_class(str(file_path))
            try:
                documents.extend(loader.load())
                logging.info(f"Successfully loaded '{file_path.name}'")
            except Exception as e:
                logging.error(f"Failed to load '{file_path.name}': {e}")
    return documents


def chunk_documents(documents: List[Document]) -> List[Document]:
    """Split documents into smaller chunks."""
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        add_start_index=True,
    )
    return text_splitter.split_documents(documents)


def store_chunks(chunks: List[Document]):
    """Store document chunks in the vector store."""
    vector_store = get_vector_store()
    logging.info(f"Storing {len(chunks)} document chunks...")

    for chunk in chunks:
        metadata = {
            "id": str(uuid.uuid4()),
            "source": "document",
            "document_name": chunk.metadata.get("source", "Unknown"),
            "start_index": chunk.metadata.get("start_index", -1),
        }
        vector_store.store_memory(text=chunk.page_content, metadata=metadata)
        logging.debug(f"Stored chunk from '{metadata['document_name']}'")

    logging.info("Document chunks stored successfully.")


async def main():
    """Main function to run the document ingestion pipeline."""
    # This function is now primarily for manual, bulk ingestion if needed.
    # The cleaning and Qdrant ingestion for new crawls is handled by graph_nodes.py

    # Define the path to the data directory for manual ingestion
    # This should point to the directory containing already cleaned documents
    MANUAL_INGESTION_DIR = Path(__file__).parent/"chatbot/data/documents" # Assuming cleaned documents are here

    if not MANUAL_INGESTION_DIR.exists():
        logging.error(f"Manual ingestion directory not found: {MANUAL_INGESTION_DIR}")
        return

    logging.info("Starting manual document ingestion...")
    documents = load_documents(MANUAL_INGESTION_DIR)
    if not documents:
        logging.warning("No documents found for manual ingestion.")
        return

    chunks = chunk_documents(documents)
    store_chunks(chunks)
    logging.info("Manual ingestion process complete.")


if __name__ == "__main__":
    # To run this script, execute `python src/ingest_documents.py` from the project root directory.
    asyncio.run(main())
