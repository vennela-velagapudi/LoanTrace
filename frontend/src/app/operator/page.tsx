export default function OperatorDashboard() {
  return (
    <div className="p-8">
      <div className="flex justify-between items-center mb-8">
        <h1 className="text-3xl font-bold tracking-tight">Operator Dashboard</h1>
        <button className="bg-primary hover:bg-blue-600 text-white px-4 py-2 rounded-md font-medium transition-colors">
          Upload New Batch
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <div className="glass-panel p-6 rounded-xl">
          <h3 className="text-[var(--muted-foreground)] font-medium mb-2">Total Uploads</h3>
          <p className="text-3xl font-bold">142</p>
        </div>
        <div className="glass-panel p-6 rounded-xl">
          <h3 className="text-[var(--muted-foreground)] font-medium mb-2">Success Rate</h3>
          <p className="text-3xl font-bold text-green-400">94.2%</p>
        </div>
        <div className="glass-panel p-6 rounded-xl">
          <h3 className="text-[var(--muted-foreground)] font-medium mb-2">Pending Exceptions</h3>
          <p className="text-3xl font-bold text-[var(--accent)]">18</p>
        </div>
      </div>

      <div className="glass-panel rounded-xl overflow-hidden">
        <div className="p-6 border-b border-[var(--border)]">
          <h2 className="text-xl font-semibold">Recent Batches</h2>
        </div>
        <div className="p-6 text-center text-[var(--muted-foreground)]">
          <p>No batches uploaded yet.</p>
          <p className="text-sm mt-2">Data ingestion features will be implemented in Phase 2.</p>
        </div>
      </div>
    </div>
  );
}
