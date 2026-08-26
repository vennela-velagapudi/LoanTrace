export default function ReviewerDashboard() {
  return (
    <div className="p-8 h-full flex flex-col">
      <div className="flex justify-between items-center mb-8">
        <h1 className="text-3xl font-bold tracking-tight">Reviewer Queue</h1>
        <div className="flex gap-4">
          <select className="bg-[var(--card)] border border-[var(--border)] rounded-md px-4 py-2 text-sm">
            <option>All Severities</option>
            <option>Critical</option>
            <option>High</option>
            <option>Warning</option>
          </select>
        </div>
      </div>

      <div className="flex-1 glass-panel rounded-xl flex overflow-hidden">
        {/* Sidebar / Queue List */}
        <div className="w-1/3 border-r border-[var(--border)] p-4 flex flex-col gap-2 overflow-y-auto">
          <div className="p-4 rounded-lg bg-[var(--card)] border border-l-4 border-l-[var(--destructive)] cursor-pointer hover:bg-[var(--secondary)] transition-colors">
            <div className="flex justify-between items-start mb-2">
              <span className="font-semibold text-sm">Loan #9021</span>
              <span className="text-xs bg-red-950 text-red-400 px-2 py-1 rounded">CRITICAL</span>
            </div>
            <p className="text-sm text-[var(--muted-foreground)]">Negative Principal Balance</p>
          </div>
          <div className="p-4 rounded-lg bg-[var(--card)] border border-[var(--border)] border-l-4 border-l-[var(--accent)] cursor-pointer hover:bg-[var(--secondary)] transition-colors opacity-50">
            <div className="flex justify-between items-start mb-2">
              <span className="font-semibold text-sm">Loan #8194</span>
              <span className="text-xs bg-purple-950 text-purple-400 px-2 py-1 rounded">HIGH</span>
            </div>
            <p className="text-sm text-[var(--muted-foreground)]">Missing Document Status</p>
          </div>
        </div>

        {/* Main Review Area */}
        <div className="flex-1 p-8 flex flex-col items-center justify-center text-[var(--muted-foreground)] relative">
          <div className="absolute top-4 right-4 ai-glow rounded-full p-2 bg-[var(--card)] text-[var(--accent)] border border-[var(--accent)]">
            ✨ AI Copilot Available
          </div>
          <p className="text-xl mb-2">Exception Workflow Pending</p>
          <p className="text-sm">The full AI review assistant and exception resolution UI will be built in Phase 3/4.</p>
        </div>
      </div>
    </div>
  );
}
