import json
from datetime import datetime
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import ChatPromptTemplate
from loguru import logger

from config import settings
from agents.state import TemporalRAGState
from utils.date_utils import parse_date_string


llm = ChatGoogleGenerativeAI(
    model=settings.main_llm_model,
    google_api_key=settings.gemini_api_key,
    temperature=0.2,
)

PROMPT = ChatPromptTemplate.from_template("""
You are a time-aware knowledge assistant. Answer the user's query using the provided document chunks.

STRICT RULES:
1. Every factual claim MUST cite its source date: "(as of [date], [source])"
2. If a fact CHANGED over time, explicitly state: "This was X in [year] but changed to Y in [year]"
3. For "latest" queries, lead with the most recent information
4. For "point_in_time" queries, only use information valid at the target date
5. Never silently blend old and new facts — always label them
6. End your response with a JSON TIMELINE block (see format below)

User Query: {query}
Temporal Intent: {temporal_intent}
Target Date: {target_date}
Conflict Resolution: {resolution}

Document Chunks (sorted newest first):
{chunks}

Respond in this exact format:

ANSWER:
[Your detailed answer here with date citations on every factual claim]

CONFIDENCE: [0.0-1.0]

TIMELINE_JSON:
[
  {{"date": "YYYY-MM-DD", "summary": "what was true at this date", "source": "filename"}},
  ...
]
""")


def build_timeline(chunks: list[dict]) -> list[dict]:
    """Build a sorted timeline from reranked chunks."""
    timeline = []
    seen_dates = set()

    for chunk in chunks:
        meta = chunk.get("metadata", {})
        date_str = meta.get("created_at", "")
        dt = parse_date_string(date_str)
        if not dt or date_str in seen_dates:
            continue
        seen_dates.add(date_str)
        timeline.append({
            "date": dt.strftime("%Y-%m-%d"),
            "summary": meta.get("text", "")[:150] + "...",
            "source": meta.get("source", "unknown"),
            "topic_hash": meta.get("topic_hash", ""),
            "is_superseded": meta.get("is_superseded", False),
        })

    timeline.sort(key=lambda x: x["date"])
    return timeline


def compute_confidence(chunks: list[dict], conflicts: list[dict]) -> float:
    """Compute overall confidence from chunk temporal confidences and conflict count."""
    if not chunks:
        return 0.0
    avg_conf = sum(
        c.get("metadata", {}).get("temporal_confidence", 0.5)
        for c in chunks[:5]
    ) / min(len(chunks), 5)
    conflict_penalty = min(0.3, len(conflicts) * 0.05)
    return round(max(0.1, avg_conf - conflict_penalty), 2)


def temporal_synthesizer_node(state: TemporalRAGState) -> TemporalRAGState:
    """Generate the final time-aware answer with citations and timeline."""
    chunks = state.get("reranked_chunks", [])

    if not chunks:
        return {
            **state,
            "final_answer": "I couldn't find any relevant documents to answer your query.",
            "timeline_report": [],
            "confidence_score": 0.0,
            "sources_used": [],
        }

    # Format top chunks for the prompt
    chunks_text = ""
    sources_used = []
    for i, chunk in enumerate(chunks[:8]):
        meta = chunk.get("metadata", {})
        date = meta.get("created_at", "unknown date")
        source = meta.get("source", "unknown")
        text = meta.get("text", "")
        score = chunk.get("final_score", 0)
        chunks_text += f"\n[{i+1}] Date: {date} | Source: {source} | Score: {score}\n{text}\n"
        sources_used.append({"date": date, "source": source, "score": score})

    try:
        chain = PROMPT | llm
        response = chain.invoke({
            "query": state["query"],
            "temporal_intent": state.get("temporal_intent", "latest"),
            "target_date": state.get("target_date") or "most recent",
            "resolution": state.get("resolution", "no conflicts"),
            "chunks": chunks_text,
        })

        raw = response.content.strip()

        # Parse answer and timeline from response
        final_answer = raw
        timeline_report = build_timeline(chunks)

        # Try to extract TIMELINE_JSON block
        if "TIMELINE_JSON:" in raw:
            parts = raw.split("TIMELINE_JSON:")
            final_answer = parts[0].replace("ANSWER:", "").strip()
            try:
                timeline_json_str = parts[1].strip()
                if timeline_json_str.startswith("```"):
                    timeline_json_str = timeline_json_str.split("```")[1]
                    if timeline_json_str.startswith("json"):
                        timeline_json_str = timeline_json_str[4:]
                parsed_timeline = json.loads(timeline_json_str.strip())
                timeline_report = parsed_timeline
            except Exception:
                pass  # Fall back to auto-built timeline

        # Extract confidence if present
        confidence = compute_confidence(chunks, state.get("conflicts", []))
        if "CONFIDENCE:" in final_answer:
            conf_parts = final_answer.split("CONFIDENCE:")
            final_answer = conf_parts[0].strip()
            try:
                confidence = float(conf_parts[1].strip().split()[0])
            except Exception:
                pass

        logger.info(f"Synthesis complete. Confidence: {confidence}")
        return {
            **state,
            "final_answer": final_answer,
            "timeline_report": timeline_report,
            "confidence_score": confidence,
            "sources_used": sources_used,
        }

    except Exception as e:
        logger.error(f"Synthesizer failed: {e}")
        return {
            **state,
            "final_answer": f"Error generating answer: {e}",
            "timeline_report": build_timeline(chunks),
            "confidence_score": 0.1,
            "sources_used": sources_used,
        }
