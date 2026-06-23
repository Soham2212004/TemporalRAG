import { useRef, useState } from 'react'
import { Upload, Link, CheckCircle, AlertCircle, Loader } from 'lucide-react'
import { useIngest } from '../hooks/useQuery'

export default function DocumentUploader() {
  const [mode, setMode] = useState<'file' | 'url'>('file')
  const [url, setUrl] = useState('')
  const [dragOver, setDragOver] = useState(false)
  const fileRef = useRef<HTMLInputElement>(null)
  const { ingestFile, ingestUrl, uploading, uploadResult, uploadError } = useIngest()

  const handleFile = async (file: File) => {
    await ingestFile(file)
  }

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault()
    setDragOver(false)
    const file = e.dataTransfer.files[0]
    if (file) handleFile(file)
  }

  const handleUrlSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (url.trim()) await ingestUrl(url.trim())
  }

  return (
    <div className="bg-slate-800/50 border border-slate-700 rounded-xl p-5 space-y-4">
      <h2 className="text-sm font-semibold text-slate-300">Ingest Documents</h2>

      {/* Mode toggle */}
      <div className="flex bg-slate-900/60 rounded-lg p-1 gap-1">
        {(['file', 'url'] as const).map(m => (
          <button
            key={m}
            onClick={() => setMode(m)}
            className={`flex-1 text-xs py-1.5 rounded-md transition-colors ${
              mode === m ? 'bg-slate-700 text-white' : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            {m === 'file' ? '📄 File Upload' : '🔗 URL'}
          </button>
        ))}
      </div>

      {mode === 'file' ? (
        <div
          onDragOver={e => { e.preventDefault(); setDragOver(true) }}
          onDragLeave={() => setDragOver(false)}
          onDrop={handleDrop}
          onClick={() => fileRef.current?.click()}
          className={`border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors ${
            dragOver ? 'border-blue-500 bg-blue-500/5' : 'border-slate-600 hover:border-slate-500'
          }`}
        >
          <Upload className="w-6 h-6 text-slate-400 mx-auto mb-2" />
          <p className="text-sm text-slate-400">Drop PDF / TXT / MD here</p>
          <p className="text-xs text-slate-600 mt-1">or click to browse</p>
          <input
            ref={fileRef}
            type="file"
            accept=".pdf,.txt,.md"
            className="hidden"
            onChange={e => e.target.files?.[0] && handleFile(e.target.files[0])}
          />
        </div>
      ) : (
        <form onSubmit={handleUrlSubmit} className="flex gap-2">
          <input
            type="url"
            value={url}
            onChange={e => setUrl(e.target.value)}
            placeholder="https://example.com/policy.html"
            className="flex-1 bg-slate-900 border border-slate-600 rounded-lg px-3 py-2 text-sm text-slate-200 placeholder-slate-500 focus:outline-none focus:border-blue-500"
          />
          <button
            type="submit"
            disabled={uploading || !url.trim()}
            className="bg-blue-600 hover:bg-blue-500 disabled:opacity-50 text-white text-sm px-4 py-2 rounded-lg transition-colors"
          >
            <Link className="w-4 h-4" />
          </button>
        </form>
      )}

      {/* Status */}
      {uploading && (
        <div className="flex items-center gap-2 text-sm text-blue-400">
          <Loader className="w-4 h-4 animate-spin" />
          Ingesting document...
        </div>
      )}
      {uploadResult && (
        <div className="flex items-start gap-2 text-sm text-emerald-400 bg-emerald-500/10 rounded-lg p-3">
          <CheckCircle className="w-4 h-4 mt-0.5 shrink-0" />
          <div>
            <div className="font-medium">{uploadResult.filename}</div>
            <div className="text-xs text-emerald-500/70">{uploadResult.chunk_count} chunks indexed · doc_id: {uploadResult.doc_id?.slice(0, 8)}...</div>
          </div>
        </div>
      )}
      {uploadError && (
        <div className="flex items-center gap-2 text-sm text-red-400 bg-red-500/10 rounded-lg p-3">
          <AlertCircle className="w-4 h-4 shrink-0" />
          {uploadError}
        </div>
      )}
    </div>
  )
}
