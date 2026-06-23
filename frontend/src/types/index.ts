export interface ConflictInfo {
  topic_id: string
  older_date: string
  newer_date: string
  gap_days: number
  severity: 'HIGH' | 'MEDIUM'
  older_text: string
  newer_text: string
}

export interface TimelineEntry {
  date: string
  summary: string
  source: string
  is_superseded?: boolean
}

export interface SourceUsed {
  date: string
  source: string
  score: number
}

export interface QueryResponse {
  query: string
  answer: string
  temporal_intent: string
  target_date: string | null
  confidence_score: number
  conflicts: ConflictInfo[]
  conflict_count: number
  timeline: TimelineEntry[]
  sources_used: SourceUsed[]
  response_time_ms: number
}

export interface IngestResponse {
  doc_id: string
  filename: string
  chunk_count: number
  source_type: string
  status: string
}
