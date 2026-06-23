import uuid
from datetime import datetime, timezone
from typing import Optional
from loguru import logger

from langchain.schema import Document

from ingestion.loader import load_from_file, load_from_url
from ingestion.chunker import chunk_documents
from ingestion.date_extractor import extract_temporal_metadata
from ingestion.topic_fingerprint import get_or_create_topic
from retrieval.pinecone_client import upsert_chunks
from utils.embedding_utils import embed_text
from utils.date_utils import parse_date_string, now_utc


def build_pinecone_metadata(
    chunk: Document,
    doc_id: str,
    source_type: str,
    temporal_meta,
    topic_hash: str,
    version_tag: str,
) -> dict:
    """Build the metadata dict that gets stored alongside the vector in Pinecone."""
    return {
        "doc_id": doc_id,
        "text": chunk.page_content[:1000],  # Pinecone metadata limit
        "source_type": source_type,
        "created_at": temporal_meta.created_at or "",
        "valid_from": temporal_meta.valid_from or "",
        "valid_until": temporal_meta.valid_until or "",
        "temporal_confidence": temporal_meta.temporal_confidence,
        "temporal_signals": ", ".join(temporal_meta.temporal_signals[:5]),
        "topic_hash": topic_hash,
        "version_tag": version_tag,
        "is_superseded": False,
        "ingested_at": now_utc().isoformat(),
        "source": chunk.metadata.get("source", ""),
    }


async def run_ingestion_pipeline(
    file_path: Optional[str] = None,
    url: Optional[str] = None,
    filename: str = "document",
    source_type_override: Optional[str] = None,
    fallback_date: Optional[str] = None,
) -> dict:
    """
    Full ingestion pipeline:
    load → chunk → extract dates → fingerprint topics → embed → upsert to Pinecone
    """
    doc_id = str(uuid.uuid4())
    logger.info(f"Starting ingestion pipeline. doc_id={doc_id}, file={filename}")

    # 1. Load
    if file_path:
        docs, source_type = load_from_file(file_path, filename)
    elif url:
        docs, source_type = load_from_url(url)
    else:
        raise ValueError("Either file_path or url must be provided.")

    if source_type_override:
        source_type = source_type_override

    # 2. Chunk
    chunks = chunk_documents(docs)
    if not chunks:
        logger.warning("No chunks produced after splitting.")
        return {"doc_id": doc_id, "chunk_count": 0, "status": "empty"}

    # 3. Process each chunk
    vectors_to_upsert = []
    chunk_records = []
    topic_versions: dict[str, int] = {}

    for i, chunk in enumerate(chunks):
        chunk_id = f"{doc_id}_chunk_{i}"

        # Extract temporal metadata
        temporal_meta = extract_temporal_metadata(
            chunk.page_content,
            fallback_date=fallback_date,
        )

        # Topic fingerprint
        topic_hash, is_new = get_or_create_topic(chunk.page_content)

        # Version tag
        if topic_hash not in topic_versions:
            topic_versions[topic_hash] = 1
        else:
            topic_versions[topic_hash] += 1
        version_tag = f"v{topic_versions[topic_hash]}"

        # Embed
        embedding = embed_text(chunk.page_content)

        # Build Pinecone record
        metadata = build_pinecone_metadata(
            chunk, doc_id, source_type, temporal_meta, topic_hash, version_tag
        )
        vectors_to_upsert.append({
            "id": chunk_id,
            "values": embedding,
            "metadata": metadata,
        })

        chunk_records.append({
            "pinecone_id": chunk_id,
            "doc_id": doc_id,
            "text": chunk.page_content,
            "temporal_meta": temporal_meta,
            "topic_hash": topic_hash,
            "version_tag": version_tag,
            "source_type": source_type,
        })

        if (i + 1) % 10 == 0:
            logger.info(f"Processed {i+1}/{len(chunks)} chunks...")

    # 4. Upsert to Pinecone in batches
    upsert_chunks(vectors_to_upsert)
    logger.info(f"Upserted {len(vectors_to_upsert)} vectors to Pinecone.")

    return {
        "doc_id": doc_id,
        "filename": filename,
        "chunk_count": len(chunks),
        "source_type": source_type,
        "status": "completed",
        "chunks": chunk_records,
    }
