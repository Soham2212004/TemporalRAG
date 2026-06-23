import os
import tempfile
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Optional
from loguru import logger

from ingestion.pipeline import run_ingestion_pipeline

router = APIRouter()


class URLIngestRequest(BaseModel):
    url: str
    source_type: Optional[str] = None
    fallback_date: Optional[str] = None


class IngestResponse(BaseModel):
    doc_id: str
    filename: str
    chunk_count: int
    source_type: str
    status: str


@router.post("/file", response_model=IngestResponse)
async def ingest_file(
    file: UploadFile = File(...),
    source_type: Optional[str] = Form(None),
    fallback_date: Optional[str] = Form(None),
):
    """Upload and ingest a PDF or text file into TemporalRAG."""
    allowed = {".pdf", ".txt", ".md"}
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in allowed:
        raise HTTPException(status_code=400, detail=f"Unsupported file type: {ext}")

    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as tmp:
            content = await file.read()
            tmp.write(content)
            tmp_path = tmp.name

        result = await run_ingestion_pipeline(
            file_path=tmp_path,
            filename=file.filename,
            source_type_override=source_type,
            fallback_date=fallback_date,
        )
        return IngestResponse(**{k: result[k] for k in IngestResponse.model_fields})

    except Exception as e:
        logger.error(f"Ingestion failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)


@router.post("/url", response_model=IngestResponse)
async def ingest_url(request: URLIngestRequest):
    """Ingest content from a web URL."""
    try:
        result = await run_ingestion_pipeline(
            url=request.url,
            filename=request.url,
            source_type_override=request.source_type,
            fallback_date=request.fallback_date,
        )
        return IngestResponse(**{k: result[k] for k in IngestResponse.model_fields})
    except Exception as e:
        logger.error(f"URL ingestion failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
