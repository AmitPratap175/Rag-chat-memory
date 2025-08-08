from pathlib import Path
from typing import List

from langchain_community.document_loaders import (
    PyPDFLoader,
    UnstructuredMarkdownLoader,
    TextLoader,
)
from langchain_core.documents import Document

FILE_LOADERS = {
    ".pdf": PyPDFLoader,
    ".md": UnstructuredMarkdownLoader,
    ".txt": TextLoader,
}


def load_documents(data_dir: Path) -> List[Document]:
    """Load all supported documents from the data directory."""
    documents = []
    for file_path in data_dir.iterdir():
        if file_path.suffix in FILE_LOADERS:
            loader_class = FILE_LOADERS[file_path.suffix]
            loader = loader_class(str(file_path))
            documents.extend(loader.load())
    return documents


