import { Clock, Zap } from 'lucide-react'
import type { QueryResponse } from '../types'
import ConfidenceBar from './ConfidenceBar'
import ConflictBadge from './ConflictBadge'
import TimelineView from './TimelineView'

interface Props {
  result: QueryResponse
}

const INTENT_LABELS: Record<string, string> = {
  latest: '🕐 Latest',
  point_in_time: '📌 Point-in-Time',
  historical_range: '📅 Historical Range',
  comparison: '⚖️ Comparison',
}

export default function AnswerCard({ result }: Props) {
  return (
    <div className="bg-slate-800/50 border border-slate-700 rounded-xl p-5 space-y-4">
      {/* Header row */}
      <div className="flex items-center justify-between flex-wrap gap-2">
        <div className="flex items-center gap-2">
          <span className="text-xs bg-slate-700 text-slate-300 px-2 py-1 rounded-full">
            {INTENT_LABELS[result.temporal_intent] ?? result.temporal_intent}
          </span>
          {result.target_date && (
            <span className="text-xs bg-blue-500/20 text-blue-300 px-2 py-1 rounded-full flex items-center gap-1">
              <Clock className="w-3 h-3" /> {result.target_date}
            </span>
          )}
        </div>
        <span className="text-xs text-slate-500 flex items-center gap-1">
          <Zap className="w-3 h-3" /> {result.response_time_ms}ms
        </span>
      </div>

      {/* Confidence */}
      <ConfidenceBar score={result.confidence_score} />

      {/* Conflicts */}
      {result.conflicts.length > 0 && <ConflictBadge conflicts={result.conflicts} />}

      {/* Answer */}
      <div className="text-slate-200 text-sm leading-relaxed whitespace-pre-wrap bg-slate-900/40 rounded-lg p-4 border border-slate-700/50">
        {result.answer}
      </div>

      {/* Timeline */}
      {result.timeline.length > 0 && <TimelineView timeline={result.timeline} />}

      {/* Sources */}
      {result.sources_used.length > 0 && (
        <div>
          <h3 className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2">Sources Used</h3>
          <div className="flex flex-wrap gap-2">
            {result.sources_used.slice(0, 5).map((s, i) => (
              <div key={i} className="text-xs bg-slate-700/50 text-slate-400 px-2 py-1 rounded border border-slate-600/50">
                <span className="font-mono">{s.date?.slice(0, 10) || 'unknown date'}</span>
                <span className="mx-1 text-slate-600">·</span>
                <span className="truncate max-w-24 inline-block align-bottom">{s.source || 'unknown'}</span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}
