import json
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import ChatPromptTemplate
from loguru import logger

from config import settings
from agents.state import TemporalRAGState


llm = ChatGoogleGenerativeAI(
    model=settings.fast_llm_model,
    google_api_key=settings.gemini_api_key,
    temperature=0,
)

PROMPT = ChatPromptTemplate.from_template("""
Analyze this user query and extract temporal intent.

Query: {query}

Classify the temporal_intent as exactly one of:
- "latest"         → user wants the most current/recent information
- "point_in_time"  → user wants info as it was at a specific past date
- "historical_range" → user wants info over a time range
- "comparison"     → user wants to compare across different time periods

Respond ONLY with a JSON object, no markdown:
{{
  "temporal_intent": "latest|point_in_time|historical_range|comparison",
  "target_date": "YYYY-MM-DD or null",
  "date_range_start": "YYYY-MM-DD or null",
  "date_range_end": "YYYY-MM-DD or null",
  "temporal_keywords": ["list", "of", "time", "related", "words", "found"]
}}
""")


def query_analyzer_node(state: TemporalRAGState) -> TemporalRAGState:
    """Detect temporal intent and extract date references from the query."""
    try:
        chain = PROMPT | llm
        response = chain.invoke({"query": state["query"]})

        raw = response.content.strip()
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]

        data = json.loads(raw)
        logger.info(f"Query analyzed: intent={data.get('temporal_intent')}, target={data.get('target_date')}")

        return {
            **state,
            "temporal_intent": data.get("temporal_intent", "latest"),
            "target_date": data.get("target_date"),
            "date_range_start": data.get("date_range_start"),
            "date_range_end": data.get("date_range_end"),
            "temporal_keywords": data.get("temporal_keywords", []),
        }

    except Exception as e:
        logger.warning(f"Query analyzer failed: {e}. Defaulting to 'latest'.")
        return {
            **state,
            "temporal_intent": "latest",
            "target_date": None,
            "date_range_start": None,
            "date_range_end": None,
            "temporal_keywords": [],
        }
