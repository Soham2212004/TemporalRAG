from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from loguru import logger

from config import settings
from api.routes import ingest, query, documents
from db.connection import init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting TemporalRAG backend...")
    await init_db()
    logger.info("Database initialized.")
    yield
    # Shutdown
    logger.info("Shutting down TemporalRAG backend.")


app = FastAPI(
    title="TemporalRAG API",
    description="Time-aware RAG system that detects knowledge conflicts across document versions",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(ingest.router, prefix="/api/ingest", tags=["Ingestion"])
app.include_router(query.router, prefix="/api/query", tags=["Query"])
app.include_router(documents.router, prefix="/api/documents", tags=["Documents"])


@app.get("/health")
async def health_check():
    return {"status": "ok", "service": "TemporalRAG"}
