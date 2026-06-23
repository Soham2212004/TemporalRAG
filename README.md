# ⏱️ TemporalRAG — Time-Aware Knowledge Base

A RAG system that treats **time as a first-class citizen**. Unlike standard RAG, TemporalRAG detects when documents contradict each other across time, resolves conflicts intelligently, and always tells you *when* something was true — not just *what* is true.

---

## The Problem It Solves

Standard RAG retrieves the most semantically similar chunks — but similarity has zero awareness of time. If you ask *"What is our refund policy?"* and you have a 2021 doc saying "30 days" and a 2024 doc saying "7 days", normal RAG may return the 2021 answer confidently. TemporalRAG solves this.

---

## Key Features

- **Temporal Decay Reranker** — scores chunks by recency using exponential decay, tunable per source type
- **Topic Fingerprinting** — groups same-topic chunks across documents to detect conflicts
- **Conflict Detection** — flags when the same topic has contradictory info from different time periods
- **LangGraph Pipeline** — 4-node agentic pipeline: QueryAnalyzer → Retriever → ConflictResolver → Synthesizer
- **Point-in-Time Queries** — ask "what was the policy in Q2 2022?" and get that exact answer
- **Timeline Reports** — every answer includes a chronological view of how the topic evolved

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | FastAPI + Python 3.11 |
| Agent Orchestration | LangGraph |
| LLM & Embeddings | Gemini 1.5 Pro / Flash + text-embedding-004 |
| Vector Store | Pinecone (serverless) |
| Database | PostgreSQL |
| Cache | Redis |
| Frontend | React + TypeScript + Tailwind |

---

## Project Structure

```
temporal-rag/
├── backend/
│   ├── main.py                    # FastAPI app entry point
│   ├── config.py                  # All settings from .env
│   ├── ingestion/
│   │   ├── loader.py              # PDF/TXT/URL document loaders
│   │   ├── chunker.py             # LangChain text splitter
│   │   ├── date_extractor.py      # Gemini Flash date extraction chain
│   │   ├── topic_fingerprint.py   # Cosine similarity topic grouping
│   │   └── pipeline.py            # Full ingestion orchestrator
│   ├── retrieval/
│   │   ├── pinecone_client.py     # Pinecone upsert/query/delete
│   │   ├── temporal_reranker.py   # Exponential decay reranker
│   │   └── conflict_detector.py   # Topic-grouped conflict detection
│   ├── agents/
│   │   ├── state.py               # LangGraph TypedDict state
│   │   ├── graph.py               # Graph wiring + compile
│   │   └── nodes/
│   │       ├── query_analyzer.py  # Temporal intent extraction
│   │       ├── retriever.py       # Embed + retrieve + rerank
│   │       ├── conflict_resolver.py # Conflict resolution strategy
│   │       └── temporal_synthesizer.py # Final answer with citations
│   ├── api/routes/
│   │   ├── ingest.py              # POST /ingest/file, /ingest/url
│   │   ├── query.py               # POST /query/, /query/point-in-time
│   │   └── documents.py           # GET /documents/stats, DELETE
│   ├── db/
│   │   ├── connection.py          # SQLAlchemy async engine
│   │   ├── models.py              # ORM models
│   │   └── migrations/001_initial.sql
│   └── utils/
│       ├── date_utils.py          # Date parsing helpers
│       └── embedding_utils.py     # Gemini embedding wrappers
└── frontend/
    └── src/
        ├── components/
        │   ├── ChatInterface.tsx   # Main chat UI
        │   ├── AnswerCard.tsx      # Answer + metadata display
        │   ├── TimelineView.tsx    # Chronological timeline
        │   ├── ConflictBadge.tsx   # Conflict warning + diff view
        │   ├── DocumentUploader.tsx # File/URL ingestion UI
        │   └── ConfidenceBar.tsx   # Confidence score bar
        └── hooks/useQuery.ts       # API call hooks
```

---

## Setup

### 1. Get API Keys

| Service | URL | Free Tier |
|---|---|---|
| Gemini API | https://aistudio.google.com | Yes |
| Pinecone | https://pinecone.io | Yes (100k vectors) |
| PostgreSQL | Docker or https://neon.tech | Yes |
| Redis | Docker or https://upstash.com | Yes |

### 2. Configure environment

```bash
cp .env.example .env
# Fill in your API keys in .env
```

### 3. Start with Docker Compose

```bash
docker-compose up -d
```

This starts PostgreSQL + Redis. Backend runs on `http://localhost:8000`.

### 4. Run backend manually (dev)

```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
```

### 5. Run frontend

```bash
cd frontend
npm install
npm run dev
# Opens at http://localhost:5173
```




## How It Works

```
User Query
    │
    ▼
QueryAnalyzer     → Detects temporal intent (latest / point-in-time / historical)
    │
    ▼
Retriever         → Embeds query → Pinecone search → Temporal decay rerank → Conflict detection
    │
    ▼
ConflictResolver  → Decides: use newer / use older / surface both / flag ambiguous
    │
    ▼
Synthesizer       → Generates answer with date citations + timeline report
```

---

