import { useState } from 'react'
import { Send, Loader, Clock } from 'lucide-react'
import { useQuery } from '../hooks/useQuery'
import AnswerCard from './AnswerCard'

export default function ChatInterface() {
  const [query, setQuery] = useState('')
  const [history, setHistory] = useState<Array<{ query: string; result: any }>>([])
  const { runQuery, loading, result, error } = useQuery()

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!query.trim() || loading) return
    const q = query.trim()
    setQuery('')
    await runQuery(q)
    setHistory(prev => [...prev, { query: q, result: null }])
  }

  // Update latest history entry with result
  if (result && history.length > 0 && !history[history.length - 1].result) {
    history[history.length - 1].result = result
  }

  const EXAMPLE_QUERIES = [
    'What is the current refund policy?',
    'What was the data retention policy in 2022?',
    'How has the pricing changed over the years?',
    'What are the current WFH rules?',
  ]

  return (
    <div className="flex flex-col h-full">
      {/* Chat history */}
      <div className="flex-1 overflow-y-auto space-y-6 pb-4">
        {history.length === 0 && (
          <div className="text-center py-12">
            <div className="text-4xl mb-3">⏱️</div>
            <h2 className="text-lg font-semibold text-slate-300 mb-1">TemporalRAG</h2>
            <p className="text-sm text-slate-500 mb-6 max-w-sm mx-auto">
              Ask anything about your documents. I'll tell you what changed, when, and which version to trust.
            </p>
            <div className="grid grid-cols-1 gap-2 max-w-md mx-auto">
              {EXAMPLE_QUERIES.map((q, i) => (
                <button
                  key={i}
                  onClick={() => setQuery(q)}
                  className="text-left text-sm text-slate-400 bg-slate-800/50 hover:bg-slate-700/50 border border-slate-700 hover:border-slate-600 rounded-lg px-4 py-2.5 transition-colors"
                >
                  <Clock className="w-3 h-3 inline mr-2 text-slate-500" />
                  {q}
                </button>
              ))}
            </div>
          </div>
        )}

        {history.map((item, i) => (
          <div key={i} className="space-y-3">
            <div className="flex justify-end">
              <div className="bg-blue-600/20 border border-blue-500/30 text-blue-200 text-sm px-4 py-2 rounded-xl max-w-lg">
                {item.query}
              </div>
            </div>
            {item.result ? (
              <AnswerCard result={item.result} />
            ) : (
              <div className="flex items-center gap-2 text-slate-400 text-sm">
                <Loader className="w-4 h-4 animate-spin" />
                Analyzing temporal context...
              </div>
            )}
          </div>
        ))}

        {loading && history.length > 0 && history[history.length - 1].result === null && (
          <div className="flex items-center gap-2 text-slate-400 text-sm pl-2">
            <Loader className="w-4 h-4 animate-spin" />
            <span>Running temporal pipeline...</span>
          </div>
        )}

        {error && (
          <div className="text-red-400 text-sm bg-red-500/10 rounded-lg px-4 py-3 border border-red-500/20">
            Error: {error}
          </div>
        )}
      </div>

      {/* Input */}
      <form onSubmit={handleSubmit} className="flex gap-3 pt-4 border-t border-slate-700">
        <input
          value={query}
          onChange={e => setQuery(e.target.value)}
          placeholder="Ask about your documents... (try 'what changed?' or 'as of 2022...')"
          className="flex-1 bg-slate-800 border border-slate-600 focus:border-blue-500 rounded-xl px-4 py-3 text-sm text-slate-200 placeholder-slate-500 outline-none transition-colors"
        />
        <button
          type="submit"
          disabled={loading || !query.trim()}
          className="bg-blue-600 hover:bg-blue-500 disabled:opacity-40 text-white px-4 py-3 rounded-xl transition-colors shrink-0"
        >
          {loading ? <Loader className="w-4 h-4 animate-spin" /> : <Send className="w-4 h-4" />}
        </button>
      </form>
    </div>
  )
}
