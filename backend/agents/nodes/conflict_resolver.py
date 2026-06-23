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
You are resolving temporal conflicts in retrieved documents.

User's temporal intent: {temporal_intent}
Target date: {target_date}

Conflicts detected:
{conflicts}

For each conflict, decide:
- "use_newer"       → trust the newer document (default for "latest" queries)
- "use_older"       → trust the older document (for point-in-time queries)
- "surface_both"    → show both versions (for comparison queries)
- "flag_ambiguous"  → unclear which to trust

Respond ONLY with a JSON object, no markdown:
{{
  "resolutions": [
    {{
      "topic_id": "...",
      "decision": "use_newer|use_older|surface_both|flag_ambiguous",
      "reasoning": "one sentence explanation"
    }}
  ],
  "overall_strategy": "brief description of how conflicts were handled"
}}
""")


def conflict_resolver_node(state: TemporalRAGState) -> TemporalRAGState:
    """Decide how to handle each detected conflict based on temporal intent."""
    if not state.get("conflicts"):
        return {**state, "resolution": "no_conflicts"}

    try:
        chain = PROMPT | llm
        response = chain.invoke({
            "temporal_intent": state.get("temporal_intent", "latest"),
            "target_date": state.get("target_date") or "not specified",
            "conflicts": json.dumps(state["conflicts"], indent=2, default=str),
        })

        raw = response.content.strip()
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]

        data = json.loads(raw)
        resolution_text = json.dumps(data)
        logger.info(f"Conflict resolution: {data.get('overall_strategy')}")
        return {**state, "resolution": resolution_text}

    except Exception as e:
        logger.warning(f"Conflict resolver failed: {e}. Using default strategy.")
        default = {
            "resolutions": [
                {"topic_id": c["topic_id"], "decision": "use_newer", "reasoning": "defaulting to newest document"}
                for c in state["conflicts"]
            ],
            "overall_strategy": "Default: using newest documents for all conflicts."
        }
        return {**state, "resolution": json.dumps(default)}
