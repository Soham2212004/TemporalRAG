import { useState } from 'react'
import axios from 'axios'
import type { QueryResponse } from '../types'

const API_BASE = '/api'

export function useQuery() {
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState<QueryResponse | null>(null)
  const [error, setError] = useState<string | null>(null)

  const runQuery = async (query: string, topK = 10) => {
    setLoading(true)
    setError(null)
    try {
      const res = await axios.post(`${API_BASE}/query/`, { query, top_k: topK })
      setResult(res.data)
    } catch (e: any) {
      setError(e.response?.data?.detail || 'Query failed')
    } finally {
      setLoading(false)
    }
  }

  return { runQuery, loading, result, error }
}

export function useIngest() {
  const [uploading, setUploading] = useState(false)
  const [uploadResult, setUploadResult] = useState<any>(null)
  const [uploadError, setUploadError] = useState<string | null>(null)

  const ingestFile = async (file: File, sourceType?: string, fallbackDate?: string) => {
    setUploading(true)
    setUploadError(null)
    const form = new FormData()
    form.append('file', file)
    if (sourceType) form.append('source_type', sourceType)
    if (fallbackDate) form.append('fallback_date', fallbackDate)
    try {
      const res = await axios.post(`${API_BASE}/ingest/file`, form)
      setUploadResult(res.data)
    } catch (e: any) {
      setUploadError(e.response?.data?.detail || 'Upload failed')
    } finally {
      setUploading(false)
    }
  }

  const ingestUrl = async (url: string) => {
    setUploading(true)
    setUploadError(null)
    try {
      const res = await axios.post(`${API_BASE}/ingest/url`, { url })
      setUploadResult(res.data)
    } catch (e: any) {
      setUploadError(e.response?.data?.detail || 'URL ingestion failed')
    } finally {
      setUploading(false)
    }
  }

  return { ingestFile, ingestUrl, uploading, uploadResult, uploadError }
}
