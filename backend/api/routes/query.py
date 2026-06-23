import time
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from loguru import logger

from agents.graph import run_pipeline

router = APIRouter()


class QueryRequest(BaseModel):
    query: str
    top_k: int = 10


class ConflictInfo(BaseModel):
    topic_id: str
    older_date: str
    newer_date: str
    gap_days: int
    severity: str
    older_text: str
    newer_text: str


class TimelineEntry(BaseModel):
    date: str
    summary: str
    source: str


class QueryResponse(BaseModel):
    query: str
    answer: str
    temporal_intent: str
    target_date: Optional[str]
    confidence_score: float
    conflicts: list
    conflict_count: int
    timeline: list
    sources_used: list
    response_time_ms: int


@router.post("/", response_model=QueryResponse)
async def query(request: QueryRequest):
    """Run a temporal-aware query against the knowledge base."""
    start = time.time()
    try:
        result = await run_pipeline(query=request.query, top_k=request.top_k)

        elapsed_ms = int((time.time() - start) * 1000)
        logger.info(f"Query completed in {elapsed_ms}ms, confidence={result.get('confidence_score')}")

        # Format conflicts for response
        formatted_conflicts = []
        for c in result.get("conflicts", []):
            formatted_conflicts.append({
                "topic_id": c.get("topic_id"),
                "older_date": c.get("older_chunk", {}).get("date", ""),
                "newer_date": c.get("newer_chunk", {}).get("date", ""),
                "gap_days": c.get("gap_days", 0),
                "severity": c.get("conflict_severity", "MEDIUM"),
                "older_text": c.get("older_chunk", {}).get("text", ""),
                "newer_text": c.get("newer_chunk", {}).get("text", ""),
            })

        return QueryResponse(
            query=request.query,
            answer=result.get("final_answer", ""),
            temporal_intent=result.get("temporal_intent", "latest"),
            target_date=result.get("target_date"),
            confidence_score=result.get("confidence_score", 0.0),
            conflicts=formatted_conflicts,
            conflict_count=len(formatted_conflicts),
            timeline=result.get("timeline_report", []),
            sources_used=result.get("sources_used", []),
            response_time_ms=elapsed_ms,
        )

    except Exception as e:
        logger.error(f"Query failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/point-in-time", response_model=QueryResponse)
async def query_point_in_time(request: QueryRequest, target_date: str):
    """
    Query the knowledge base as it existed at a specific date.
    Useful for audits, legal reviews, historical analysis.
    """
    # Inject point-in-time hint into the query
    modified_query = f"{request.query} [as of {target_date}]"
    start = time.time()
    try:
        result = await run_pipeline(query=modified_query, top_k=request.top_k)
        elapsed_ms = int((time.time() - start) * 1000)

        return QueryResponse(
            query=request.query,
            answer=result.get("final_answer", ""),
            temporal_intent="point_in_time",
            target_date=target_date,
            confidence_score=result.get("confidence_score", 0.0),
            conflicts=[],
            conflict_count=0,
            timeline=result.get("timeline_report", []),
            sources_used=result.get("sources_used", []),
            response_time_ms=elapsed_ms,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
