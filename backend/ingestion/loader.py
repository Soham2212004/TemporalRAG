import os
import tempfile
from typing import Tuple
from pathlib import Path
from loguru import logger

from langchain_community.document_loaders import (
    PyPDFLoader,
    TextLoader,
    WebBaseLoader,
)
from langchain.schema import Document


SUPPORTED_EXTENSIONS = {".pdf", ".txt", ".md"}


def load_from_file(file_path: str, filename: str) -> Tuple[list[Document], str]:
    """Load documents from a file. Returns (docs, source_type)."""
    ext = Path(filename).suffix.lower()

    if ext not in SUPPORTED_EXTENSIONS:
        raise ValueError(f"Unsupported file type: {ext}. Supported: {SUPPORTED_EXTENSIONS}")

    try:
        if ext == ".pdf":
            loader = PyPDFLoader(file_path)
            source_type = "pdf"
        else:
            loader = TextLoader(file_path, encoding="utf-8")
            source_type = "text"

        docs = loader.load()
        logger.info(f"Loaded {len(docs)} pages/sections from {filename}")
        return docs, source_type

    except Exception as e:
        logger.error(f"Failed to load file {filename}: {e}")
        raise


def load_from_url(url: str) -> Tuple[list[Document], str]:
    """Load document from a URL."""
    try:
        loader = WebBaseLoader(url)
        docs = loader.load()
        logger.info(f"Loaded {len(docs)} sections from URL: {url}")
        return docs, "web"
    except Exception as e:
        logger.error(f"Failed to load URL {url}: {e}")
        raise


def load_from_text(text: str, source_name: str = "manual") -> Tuple[list[Document], str]:
    """Load from raw text string."""
    doc = Document(page_content=text, metadata={"source": source_name})
    return [doc], "text"
