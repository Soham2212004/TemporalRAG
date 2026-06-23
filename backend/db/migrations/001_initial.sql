-- Documents registry
CREATE TABLE IF NOT EXISTS documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    filename TEXT NOT NULL,
    source_url TEXT,
    source_type TEXT DEFAULT 'unknown',
    ingested_at TIMESTAMPTZ DEFAULT NOW(),
    chunk_count INTEGER DEFAULT 0,
    status TEXT DEFAULT 'pending',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Chunks metadata (mirrors Pinecone metadata for SQL queries)
CREATE TABLE IF NOT EXISTS chunks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    doc_id UUID REFERENCES documents(id) ON DELETE CASCADE,
    pinecone_id TEXT UNIQUE NOT NULL,
    text TEXT NOT NULL,
    source_type TEXT DEFAULT 'unknown',
    created_at_doc TIMESTAMPTZ,
    ingested_at TIMESTAMPTZ DEFAULT NOW(),
    valid_from TIMESTAMPTZ,
    valid_until TIMESTAMPTZ,
    is_superseded BOOLEAN DEFAULT FALSE,
    superseded_by UUID,
    temporal_confidence FLOAT DEFAULT 0.5,
    topic_hash TEXT,
    version_tag TEXT DEFAULT 'v1',
    temporal_signals JSONB DEFAULT '[]'
);

-- Topic centroids
CREATE TABLE IF NOT EXISTS topics (
    id TEXT PRIMARY KEY,
    centroid JSONB NOT NULL,
    chunk_count INTEGER DEFAULT 1,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Conflict log
CREATE TABLE IF NOT EXISTS conflicts_log (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    query_id UUID,
    topic_id TEXT,
    older_chunk_id TEXT,
    newer_chunk_id TEXT,
    gap_days INTEGER,
    conflict_severity TEXT,
    resolution TEXT,
    detected_at TIMESTAMPTZ DEFAULT NOW()
);

-- Query log
CREATE TABLE IF NOT EXISTS query_log (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    query TEXT NOT NULL,
    temporal_intent TEXT,
    target_date TEXT,
    final_answer TEXT,
    confidence_score FLOAT,
    conflict_count INTEGER DEFAULT 0,
    response_time_ms INTEGER,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_chunks_doc_id ON chunks(doc_id);
CREATE INDEX IF NOT EXISTS idx_chunks_topic_hash ON chunks(topic_hash);
CREATE INDEX IF NOT EXISTS idx_chunks_created_at ON chunks(created_at_doc);
CREATE INDEX IF NOT EXISTS idx_chunks_is_superseded ON chunks(is_superseded);
CREATE INDEX IF NOT EXISTS idx_query_log_created_at ON query_log(created_at);
