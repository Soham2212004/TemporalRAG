from langgraph.graph import StateGraph, END
from agents.state import TemporalRAGState
from agents.nodes.query_analyzer import query_analyzer_node
from agents.nodes.retriever import retriever_node
from agents.nodes.conflict_resolver import conflict_resolver_node
from agents.nodes.temporal_synthesizer import temporal_synthesizer_node
from loguru import logger


def build_graph():
    graph = StateGraph(TemporalRAGState)

    graph.add_node("query_analyzer", query_analyzer_node)
    graph.add_node("retriever", retriever_node)
    graph.add_node("conflict_resolver", conflict_resolver_node)
    graph.add_node("temporal_synthesizer", temporal_synthesizer_node)

    graph.set_entry_point("query_analyzer")
    graph.add_edge("query_analyzer", "retriever")
    graph.add_edge("retriever", "conflict_resolver")
    graph.add_edge("conflict_resolver", "temporal_synthesizer")
    graph.add_edge("temporal_synthesizer", END)

    compiled = graph.compile()
    logger.info("TemporalRAG LangGraph pipeline compiled.")
    return compiled


temporal_rag_pipeline = build_graph()


async def run_pipeline(query: str, top_k: int = 10) -> TemporalRAGState:
    initial_state: TemporalRAGState = {
        "query": query,
        "top_k": top_k,
        "temporal_intent": "latest",
        "target_date": None,
        "date_range_start": None,
        "date_range_end": None,
        "temporal_keywords": [],
        "retrieved_chunks": [],
        "reranked_chunks": [],
        "conflicts": [],
        "resolution": "",
        "final_answer": "",
        "timeline_report": [],
        "confidence_score": 0.0,
        "sources_used": [],
        "error": None,
    }
    result = await temporal_rag_pipeline.ainvoke(initial_state)
    return result
