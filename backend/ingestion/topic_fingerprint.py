import json
import uuid
from typing import Optional
from loguru import logger

from utils.embedding_utils import embed_text, cosine_similarity, average_vectors
from config import settings


# In-memory topic store for the session
# In production this syncs with the topics PostgreSQL table
_topic_store: dict[str, list[float]] = {}


def load_topics_from_db(topics: list[dict]):
    """Load existing topic centroids from DB into memory."""
    global _topic_store
    for t in topics:
        if t.get("centroid"):
            _topic_store[t["id"]] = t["centroid"]
    logger.info(f"Loaded {len(_topic_store)} topics into memory.")


def get_or_create_topic(chunk_text: str) -> tuple[str, bool]:
    """
    Embeds the chunk and compares against existing topic centroids.
    Returns (topic_id, is_new_topic).

    If cosine similarity > threshold → same topic (conflict candidate).
    Otherwise → new topic.
    """
    global _topic_store

    chunk_embedding = embed_text(chunk_text)

    best_match_id = None
    best_similarity = 0.0

    for topic_id, centroid in _topic_store.items():
        sim = cosine_similarity(chunk_embedding, centroid)
        if sim > best_similarity:
            best_similarity = sim
            best_match_id = topic_id

    if best_similarity >= settings.topic_similarity_threshold:
        # Update centroid (running average)
        old_centroid = _topic_store[best_match_id]
        new_centroid = average_vectors([old_centroid, chunk_embedding])
        _topic_store[best_match_id] = new_centroid
        logger.debug(f"Chunk matched topic {best_match_id} (similarity: {best_similarity:.3f})")
        return best_match_id, False

    # New topic
    new_topic_id = f"topic_{uuid.uuid4().hex[:8]}"
    _topic_store[new_topic_id] = chunk_embedding
    logger.debug(f"New topic created: {new_topic_id}")
    return new_topic_id, True


def get_all_topics() -> dict[str, list[float]]:
    return _topic_store.copy()
