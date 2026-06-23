from pinecone import Pinecone, ServerlessSpec
from typing import Optional
from loguru import logger
from config import settings

_pc: Optional[Pinecone] = None
_index = None


def get_pinecone_index():
    global _pc, _index
    if _index is None:
        _pc = Pinecone(api_key=settings.pinecone_api_key)

        existing = [i.name for i in _pc.list_indexes()]
        if settings.pinecone_index_name not in existing:
            logger.info(f"Creating Pinecone index: {settings.pinecone_index_name}")
            _pc.create_index(
                name=settings.pinecone_index_name,
                dimension=settings.embedding_dimension,
                metric="cosine",
                spec=ServerlessSpec(cloud="aws", region=settings.pinecone_environment),
            )

        _index = _pc.Index(settings.pinecone_index_name)
        logger.info(f"Pinecone index ready: {settings.pinecone_index_name}")
    return _index


def upsert_chunks(vectors: list[dict], batch_size: int = 100):
    """Upsert vectors to Pinecone in batches."""
    index = get_pinecone_index()
    for i in range(0, len(vectors), batch_size):
        batch = vectors[i:i + batch_size]
        index.upsert(vectors=batch)
        logger.debug(f"Upserted batch {i//batch_size + 1} ({len(batch)} vectors)")


def query_similar(
    query_embedding: list[float],
    top_k: int = 10,
    filter_metadata: Optional[dict] = None,
) -> list[dict]:
    """Query Pinecone for similar vectors with optional metadata filter."""
    index = get_pinecone_index()
    results = index.query(
        vector=query_embedding,
        top_k=top_k,
        include_metadata=True,
        filter=filter_metadata,
    )
    return results.get("matches", [])


def delete_by_doc_id(doc_id: str):
    """Delete all vectors for a document."""
    index = get_pinecone_index()
    index.delete(filter={"doc_id": {"$eq": doc_id}})
    logger.info(f"Deleted all vectors for doc_id: {doc_id}")


def get_index_stats() -> dict:
    index = get_pinecone_index()
    return index.describe_index_stats()
