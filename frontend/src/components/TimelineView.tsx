import type { TimelineEntry } from '../types'

interface Props {
  timeline: TimelineEntry[]
}

export default function TimelineView({ timeline }: Props) {
  if (!timeline.length) return null

  return (
    <div className="mt-4">
      <h3 className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-3">Knowledge Timeline</h3>
      <div className="relative">
        {/* Line */}
        <div className="absolute left-3 top-0 bottom-0 w-px bg-slate-700" />

        <div className="space-y-3">
          {timeline.map((entry, i) => {
            const isLast = i === timeline.length - 1
            return (
              <div key={i} className="flex gap-4 relative pl-8">
                {/* Dot */}
                <div className={`absolute left-0 w-6 h-6 rounded-full border-2 flex items-center justify-center text-xs
                  ${isLast
                    ? 'bg-emerald-500/20 border-emerald-500 text-emerald-400'
                    : entry.is_superseded
                      ? 'bg-slate-800 border-slate-600 text-slate-500'
                      : 'bg-slate-800 border-slate-500 text-slate-400'
                  }`}>
                  {isLast ? '★' : '·'}
                </div>

                <div className={`flex-1 pb-1 ${entry.is_superseded ? 'opacity-50' : ''}`}>
                  <div className="flex items-center gap-2 mb-0.5">
                    <span className="text-xs font-mono text-slate-400">{entry.date}</span>
                    {entry.is_superseded && (
                      <span className="text-xs bg-slate-700 text-slate-500 px-1.5 rounded">superseded</span>
                    )}
                    {isLast && (
                      <span className="text-xs bg-emerald-500/20 text-emerald-400 px-1.5 rounded">current</span>
                    )}
                  </div>
                  <p className="text-sm text-slate-300 leading-relaxed">{entry.summary}</p>
                  <p className="text-xs text-slate-500 mt-0.5 truncate">{entry.source}</p>
                </div>
              </div>
            )
          })}
        </div>
      </div>
    </div>
  )
}
