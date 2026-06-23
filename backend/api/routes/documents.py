from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from loguru import logger

from retrieval.pinecone_client import delete_by_doc_id, get_index_stats

router = APIRouter()


class DocumentInfo(BaseModel):
    doc_id: str
    filename: str
    source_type: str
    chunk_count: int
    status: str


class IndexStats(BaseModel):
    total_vectors: int
    index_name: str


@router.get("/stats")
async def get_stats():
    """Get Pinecone index statistics."""
    try:
        stats = get_index_stats()
        return {
            "total_vectors": stats.get("total_vector_count", 0),
            "namespaces": stats.get("namespaces", {}),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{doc_id}")
async def delete_document(doc_id: str):
    """Remove a document and all its vectors from the index."""
    try:
        delete_by_doc_id(doc_id)
        return {"message": f"Document {doc_id} deleted successfully."}
    except Exception as e:
        logger.error(f"Delete failed for doc {doc_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))
