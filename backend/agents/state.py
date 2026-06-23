from typing import TypedDict, Optional, Any


class TemporalRAGState(TypedDict):
    # Input
    query: str
    top_k: int

    # Query analysis
    temporal_intent: str          # "latest" | "point_in_time" | "historical_range" | "comparison"
    target_date: Optional[str]    # for point-in-time queries
    date_range_start: Optional[str]
    date_range_end: Optional[str]
    temporal_keywords: list[str]

    # Retrieval
    retrieved_chunks: list[dict]
    reranked_chunks: list[dict]

    # Conflict analysis
    conflicts: list[dict]
    resolution: str

    # Output
    final_answer: str
    timeline_report: list[dict]
    confidence_score: float
    sources_used: list[dict]

    # Meta
    error: Optional[str]
