interface Props {
  score: number
}

export default function ConfidenceBar({ score }: Props) {
  const pct = Math.round(score * 100)
  const color = pct >= 80 ? 'bg-emerald-500' : pct >= 50 ? 'bg-amber-500' : 'bg-red-500'
  const label = pct >= 80 ? 'High' : pct >= 50 ? 'Medium' : 'Low'

  return (
    <div className="flex items-center gap-3">
      <span className="text-xs text-slate-400 w-20">Confidence</span>
      <div className="flex-1 bg-slate-700 rounded-full h-2">
        <div className={`${color} h-2 rounded-full transition-all`} style={{ width: `${pct}%` }} />
      </div>
      <span className="text-xs font-mono text-slate-300 w-16">{label} {pct}%</span>
    </div>
  )
}
