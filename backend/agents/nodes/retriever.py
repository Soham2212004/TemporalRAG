from loguru import logger
from agents.state import TemporalRAGState
from retrieval.pinecone_client import query_similar
from utils.embedding_utils import embed_query
from utils.date_utils import parse_date_string
from collections import defaultdict
import math
from datetime import datetime, timezone


DECAY_RATES = {
    "policy": 0.15, "research": 0.03, "changelog": 0.20,
    "news": 0.25, "pdf": 0.15, "web": 0.25,
    "text": 0.10, "unknown": 0.10,
}


def _temporal_decay(chunk_date, source_type="unknown"):
    if chunk_date is None:
        return 0.4
    now = datetime.now(timezone.utc)
    if chunk_date.tzinfo is None:
        chunk_date = chunk_date.replace(tzinfo=timezone.utc)
    days_old = max(0, (now - chunk_date).days)
    rate = DECAY_RATES.get(source_type, 0.10)
    return round(math.exp(-rate * (days_old / 365)), 4)


def _rerank(raw_chunks, temporal_intent="latest"):
    scored = []
    for raw in raw_chunks:
        chunk = raw.to_dict() if hasattr(raw, 'to_dict') else dict(raw)
        meta = chunk.get("metadata", {})
        semantic_score = float(chunk.get("score", 0.5))
        date_str = meta.get("created_at", "")
        chunk_date = parse_date_string(date_str)
        source_type = meta.get("source_type", "unknown")
        is_superseded = bool(meta.get("is_superseded", False))
        time_score = _temporal_decay(chunk_date, source_type)
        penalty = 0.3 if is_superseded else 1.0
        final_score = round(((0.6 * semantic_score) + (0.4 * time_score)) * penalty, 4)
        new_chunk = dict(chunk)
        new_chunk["temporal_score"] = time_score
        new_chunk["semantic_score"] = semantic_score
        new_chunk["final_score"] = final_score
        new_chunk["chunk_date"] = chunk_date.isoformat() if chunk_date else None
        scored.append(new_chunk)
    scored.sort(key=lambda x: x["final_score"], reverse=True)
    return scored


def _detect_conflicts(chunks):
    topic_groups = defaultdict(list)
    for chunk in chunks:
        meta = chunk.get("metadata", {})
        topic_hash = meta.get("topic_hash")
        if topic_hash:
            topic_groups[topic_hash].append(chunk)

    conflicts = []
    for topic_id, group in topic_groups.items():
        if len(group) < 2:
            continue
        dated = []
        for c in group:
            d = parse_date_string(c.get("metadata", {}).get("created_at", ""))
            if d:
                dated.append((d, c))
        if len(dated) < 2:
            continue
        dated.sort(key=lambda x: x[0])
        oldest_dt, oldest = dated[0]
        newest_dt, newest = dated[-1]
        gap = abs((newest_dt - oldest_dt).days)
        if gap >= 90:
            conflicts.append({
                "topic_id": topic_id,
                "older_chunk": {
                    "id": oldest.get("id"),
                    "text": oldest.get("metadata", {}).get("text", "")[:300],
                    "date": oldest_dt.isoformat(),
                    "source": oldest.get("metadata", {}).get("source", ""),
                    "score": oldest.get("final_score", 0),
                },
                "newer_chunk": {
                    "id": newest.get("id"),
                    "text": newest.get("metadata", {}).get("text", "")[:300],
                    "date": newest_dt.isoformat(),
                    "source": newest.get("metadata", {}).get("source", ""),
                    "score": newest.get("final_score", 0),
                },
                "gap_days": gap,
                "conflict_severity": "HIGH" if gap > 365 else "MEDIUM",
            })
            logger.info(f"Conflict: topic={topic_id}, gap={gap} days")
    return conflicts


def retriever_node(state: TemporalRAGState) -> TemporalRAGState:
    try:
        query_embedding = embed_query(state["query"])

        pinecone_filter = None
        if state.get("temporal_intent") == "point_in_time" and state.get("target_date"):
            pinecone_filter = {"created_at": {"$lte": state["target_date"]}}

        raw_chunks = query_similar(
            query_embedding=query_embedding,
            top_k=state.get("top_k", 10),
            filter_metadata=pinecone_filter,
        )
        logger.info(f"Retrieved {len(raw_chunks)} raw chunks from Pinecone.")

        if not raw_chunks:
            return {**state, "retrieved_chunks": [], "reranked_chunks": [], "conflicts": []}

        reranked = _rerank(raw_chunks, state.get("temporal_intent", "latest"))
        conflicts = _detect_conflicts(reranked)
        logger.info(f"Detected {len(conflicts)} conflicts.")

        return {
            **state,
            "retrieved_chunks": [r.to_dict() if hasattr(r, 'to_dict') else r for r in raw_chunks],
            "reranked_chunks": reranked,
            "conflicts": conflicts,
        }

    except Exception as e:
        logger.error(f"Retriever node failed: {e}")
        import traceback
        traceback.print_exc()
        return {
            **state,
            "retrieved_chunks": [],
            "reranked_chunks": [],
            "conflicts": [],
            "error": str(e),
        }
