from collections import defaultdict
from typing import Optional
from loguru import logger

from config import settings
from utils.date_utils import parse_date_string, days_between


def detect_conflicts(reranked_chunks: list[dict]) -> list[dict]:
    """
    Groups chunks by topic_hash.
    For groups with 2+ chunks from different time periods (gap > threshold),
    creates a conflict record.
    """
    topic_groups: dict[str, list[dict]] = defaultdict(list)

    for chunk in reranked_chunks:
        meta = chunk.get("metadata", {})
        topic_hash = meta.get("topic_hash")
        if topic_hash:
            topic_groups[topic_hash].append(chunk)

    conflicts = []

    for topic_id, chunks in topic_groups.items():
        if len(chunks) < 2:
            continue

        # Sort by date
        dated_chunks = []
        for c in chunks:
            date_str = c.get("metadata", {}).get("created_at", "")
            dt = parse_date_string(date_str)
            dated_chunks.append((dt, c))

        # Filter out undated
        dated_chunks = [(dt, c) for dt, c in dated_chunks if dt is not None]
        if len(dated_chunks) < 2:
            continue

        dated_chunks.sort(key=lambda x: x[0])
        oldest_dt, oldest_chunk = dated_chunks[0]
        newest_dt, newest_chunk = dated_chunks[-1]

        gap_days = days_between(oldest_dt, newest_dt)

        if gap_days >= settings.conflict_threshold_days:
            severity = "HIGH" if gap_days > 365 else "MEDIUM"

            conflicts.append({
                "topic_id": topic_id,
                "older_chunk": {
                    "id": oldest_chunk.get("id"),
                    "text": oldest_chunk.get("metadata", {}).get("text", "")[:300],
                    "date": oldest_dt.isoformat(),
                    "source": oldest_chunk.get("metadata", {}).get("source", ""),
                    "score": oldest_chunk.get("final_score", 0),
                },
                "newer_chunk": {
                    "id": newest_chunk.get("id"),
                    "text": newest_chunk.get("metadata", {}).get("text", "")[:300],
                    "date": newest_dt.isoformat(),
                    "source": newest_chunk.get("metadata", {}).get("source", ""),
                    "score": newest_chunk.get("final_score", 0),
                },
                "gap_days": gap_days,
                "conflict_severity": severity,
                "all_versions_count": len(dated_chunks),
            })

            logger.info(
                f"Conflict detected on topic {topic_id}: "
                f"{gap_days} day gap, severity={severity}"
            )

    return conflicts
