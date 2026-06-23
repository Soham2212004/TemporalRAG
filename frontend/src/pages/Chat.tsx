import ChatInterface from '../components/ChatInterface'
import DocumentUploader from '../components/DocumentUploader'

export default function Chat() {
  return (
    <div className="flex h-screen bg-slate-900 text-white overflow-hidden">
      {/* Sidebar */}
      <aside className="w-80 shrink-0 border-r border-slate-700 p-4 overflow-y-auto">
        <div className="mb-6">
          <h1 className="text-lg font-bold text-white flex items-center gap-2">
            <span>⏱️</span> TemporalRAG
          </h1>
          <p className="text-xs text-slate-500 mt-1">Time-aware knowledge base</p>
        </div>
        <DocumentUploader />
      </aside>

      {/* Chat */}
      <main className="flex-1 flex flex-col p-6 min-w-0">
        <ChatInterface />
      </main>
    </div>
  )
}
