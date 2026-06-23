from sqlalchemy import Column, String, Boolean, Float, Integer, Text, TIMESTAMP, JSON, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from db.connection import Base
import uuid


class Document(Base):
    __tablename__ = "documents"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    filename = Column(Text, nullable=False)
    source_url = Column(Text, nullable=True)
    source_type = Column(String(50), default="unknown")
    ingested_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    chunk_count = Column(Integer, default=0)
    status = Column(String(20), default="pending")
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())


class Chunk(Base):
    __tablename__ = "chunks"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    doc_id = Column(UUID(as_uuid=True), ForeignKey("documents.id", ondelete="CASCADE"))
    pinecone_id = Column(Text, unique=True, nullable=False)
    text = Column(Text, nullable=False)
    source_type = Column(String(50), default="unknown")
    created_at_doc = Column(TIMESTAMP(timezone=True), nullable=True)
    ingested_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    valid_from = Column(TIMESTAMP(timezone=True), nullable=True)
    valid_until = Column(TIMESTAMP(timezone=True), nullable=True)
    is_superseded = Column(Boolean, default=False)
    superseded_by = Column(UUID(as_uuid=True), nullable=True)
    temporal_confidence = Column(Float, default=0.5)
    topic_hash = Column(String(100), nullable=True)
    version_tag = Column(String(20), default="v1")
    temporal_signals = Column(JSON, default=list)


class Topic(Base):
    __tablename__ = "topics"

    id = Column(Text, primary_key=True)
    centroid = Column(JSON, nullable=False)
    chunk_count = Column(Integer, default=1)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now())


class ConflictLog(Base):
    __tablename__ = "conflicts_log"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    query_id = Column(UUID(as_uuid=True), nullable=True)
    topic_id = Column(Text, nullable=True)
    older_chunk_id = Column(Text, nullable=True)
    newer_chunk_id = Column(Text, nullable=True)
    gap_days = Column(Integer, nullable=True)
    conflict_severity = Column(String(20), nullable=True)
    resolution = Column(Text, nullable=True)
    detected_at = Column(TIMESTAMP(timezone=True), server_default=func.now())


class QueryLog(Base):
    __tablename__ = "query_log"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    query = Column(Text, nullable=False)
    temporal_intent = Column(String(50), nullable=True)
    target_date = Column(Text, nullable=True)
    final_answer = Column(Text, nullable=True)
    confidence_score = Column(Float, nullable=True)
    conflict_count = Column(Integer, default=0)
    response_time_ms = Column(Integer, nullable=True)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
