import math
from datetime import datetime, timezone
from typing import Optional
from loguru import logger

from config import settings
from utils.date_utils import parse_date_string, days_between, now_utc


DECAY_RATES = {
    "policy": settings.decay_rate_policy,
    "research": settings.decay_rate_research,
    "changelog": settings.decay_rate_changelog,
    "news": settings.decay_rate_news,
    "pdf": settings.decay_rate_policy,
    "web": settings.decay_rate_news,
    "text": settings.decay_rate_default,
    "unknown": settings.decay_rate_default,
}


def temporal_decay(
    chunk_date: Optional[datetime],
    reference_date: Optional[datetime] = None,
    source_type: str = "unknown",
) -> float:
    """
    Compute exponential temporal decay score [0.0 - 1.0].
    Newer documents score higher. Rate depends on source type.
    """
    if chunk_date is None:
        return 0.4  # no date info — neutral-low score

    ref = reference_date or now_utc()
    if chunk_date.tzinfo is None:
        chunk_date = chunk_date.replace(tzinfo=timezone.utc)
    if ref.tzinfo is None:
        ref = ref.replace(tzinfo=timezone.utc)

    days_old = max(0, (ref - chunk_date).days)
    rate = DECAY_RATES.get(source_type, settings.decay_rate_default)
    score = math.exp(-rate * (days_old / 365))
    return round(score, 4)


def rerank_chunks(
    raw_chunks: list[dict],
    temporal_weight: float = 0.4,
    target_date: Optional[str] = None,
    temporal_intent: str = "latest",
) -> list[dict]:
    """
    Rerank Pinecone results by combining semantic score + temporal decay.

    temporal_weight: 0.0 = pure semantic, 1.0 = pure temporal
    For point-in-time queries, we INVERT decay (older = closer to target = better)
    """
    reference_date = parse_date_string(target_date) if target_date else now_utc()

    scored = []
    for chunk in raw_chunks:
        meta = chunk.get("metadata", {})
        semantic_score = chunk.get("score", 0.5)

        created_at_str = meta.get("created_at", "")
        chunk_date = parse_date_string(created_at_str)
        source_type = meta.get("source_type", "unknown")
        is_superseded = meta.get("is_superseded", False)

        if temporal_intent == "point_in_time" and target_date and chunk_date:
            # Score by closeness to target date rather than recency
            days_diff = abs(days_between(chunk_date, reference_date))
            proximity_score = math.exp(-0.01 * days_diff)
            time_score = proximity_score
        else:
            time_score = temporal_decay(chunk_date, reference_date, source_type)

        # Penalty for superseded chunks
        superseded_penalty = 0.3 if is_superseded else 1.0

        final_score = (
            (1 - temporal_weight) * semantic_score +
            temporal_weight * time_score
        ) * superseded_penalty

        scored.append({
            **chunk,
            "temporal_score": time_score,
            "semantic_score": semantic_score,
            "final_score": round(final_score, 4),
            "chunk_date": chunk_date.isoformat() if chunk_date else None,
        })

    scored.sort(key=lambda x: x["final_score"], reverse=True)
    logger.debug(f"Reranked {len(scored)} chunks. Top score: {scored[0]['final_score'] if scored else 'N/A'}")
    return scored
