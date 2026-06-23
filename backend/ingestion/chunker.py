from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document
from typing import List
from loguru import logger


def chunk_documents(
    docs: List[Document],
    chunk_size: int = 512,
    chunk_overlap: int = 50,
) -> List[Document]:
    """
    Split documents into chunks with overlap.
    Inherits all metadata from parent document.
    """
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        length_function=len,
        separators=["\n\n", "\n", ". ", " ", ""],
    )

    chunks = splitter.split_documents(docs)
    logger.info(f"Split {len(docs)} documents into {len(chunks)} chunks.")

    # Filter out empty/too-short chunks
    filtered = [c for c in chunks if len(c.page_content.strip()) > 50]
    logger.info(f"After filtering: {len(filtered)} valid chunks.")

    return filtered
