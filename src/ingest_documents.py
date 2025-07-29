import asyncio
import logging
# import os
# import sys
# # Add the project root directory to the Python path
# sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')))

import uuid
from pathlib import Path
from typing import List

from src.ai_companion.modules.memory.long_term.vector_store import get_vector_store
from langchain_community.document_loaders import (
    PyPDFLoader,
    UnstructuredMarkdownLoader,
)
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Define the path to the data directory
DATA_DIR = Path("/home/dspratap/Documents/GithubProjects/Rag-chat-memory/src/ai_companion/data")

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
    if not DATA_DIR.exists():
        logging.error(f"Data directory not found: {DATA_DIR}")
        return

    logging.info("Starting document ingestion...")
    documents = load_documents(DATA_DIR)
    if not documents:
        logging.warning("No documents found to ingest.")
        return

    chunks = chunk_documents(documents)
    store_chunks(chunks)
    logging.info("Ingestion process complete.")


if __name__ == "__main__":
    # To run this script, execute `python -m scripts.ingest_documents` from the `src/ai_companion` directory.
    asyncio.run(main())
