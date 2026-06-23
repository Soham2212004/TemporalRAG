import google.generativeai as genai
import numpy as np
from typing import List
from config import settings
from loguru import logger

genai.configure(api_key=settings.gemini_api_key)


def embed_text(text: str) -> List[float]:
    try:
        result = genai.embed_content(
            model="models/gemini-embedding-001",
            content=text,
            task_type="retrieval_document",
        )
        return result["embedding"]
    except Exception as e:
        logger.error(f"Embedding error: {e}")
        raise


def embed_query(text: str) -> List[float]:
    try:
        result = genai.embed_content(
            model="models/gemini-embedding-001",
            content=text,
            task_type="retrieval_query",
        )
        return result["embedding"]
    except Exception as e:
        logger.error(f"Query embedding error: {e}")
        raise


def cosine_similarity(vec1: List[float], vec2: List[float]) -> float:
    a = np.array(vec1)
    b = np.array(vec2)
    if np.linalg.norm(a) == 0 or np.linalg.norm(b) == 0:
        return 0.0
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))


def average_vectors(vectors: List[List[float]]) -> List[float]:
    if not vectors:
        return []
    arr = np.array(vectors)
    return arr.mean(axis=0).tolist()