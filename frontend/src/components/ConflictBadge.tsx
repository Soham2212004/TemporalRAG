import { useState } from 'react'
import { AlertTriangle, ChevronDown, ChevronUp } from 'lucide-react'
import type { ConflictInfo } from '../types'

interface Props {
  conflicts: ConflictInfo[]
}

export default function ConflictBadge({ conflicts }: Props) {
  const [expanded, setExpanded] = useState(false)

  if (!conflicts.length) return null

  const highCount = conflicts.filter(c => c.severity === 'HIGH').length

  return (
    <div className="border border-amber-500/40 rounded-lg bg-amber-500/5 overflow-hidden">
      <button
        onClick={() => setExpanded(!expanded)}
        className="w-full flex items-center gap-3 p-3 text-left hover:bg-amber-500/10 transition-colors"
      >
        <AlertTriangle className="w-4 h-4 text-amber-400 shrink-0" />
        <span className="text-sm text-amber-300 font-medium flex-1">
          {conflicts.length} temporal conflict{conflicts.length > 1 ? 's' : ''} detected
          {highCount > 0 && <span className="ml-2 text-xs bg-red-500/20 text-red-400 px-2 py-0.5 rounded-full">{highCount} HIGH</span>}
        </span>
        {expanded ? <ChevronUp className="w-4 h-4 text-slate-400" /> : <ChevronDown className="w-4 h-4 text-slate-400" />}
      </button>

      {expanded && (
        <div className="px-3 pb-3 space-y-3">
          {conflicts.map((c, i) => (
            <div key={i} className="grid grid-cols-2 gap-2 text-xs">
              <div className="bg-slate-800/60 rounded p-2 border border-red-500/20">
                <div className="text-red-400 font-mono mb-1">📄 Older — {c.older_date?.slice(0, 10)}</div>
                <div className="text-slate-300 leading-relaxed">{c.older_text?.slice(0, 160)}...</div>
              </div>
              <div className="bg-slate-800/60 rounded p-2 border border-emerald-500/20">
                <div className="text-emerald-400 font-mono mb-1">📄 Newer — {c.newer_date?.slice(0, 10)}</div>
                <div className="text-slate-300 leading-relaxed">{c.newer_text?.slice(0, 160)}...</div>
              </div>
              <div className="col-span-2 text-slate-500 text-center">
                Gap: {c.gap_days} days &nbsp;·&nbsp; Severity:
                <span className={c.severity === 'HIGH' ? ' text-red-400' : ' text-amber-400'}> {c.severity}</span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
