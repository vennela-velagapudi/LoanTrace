export default function ConsumerDashboard() {
  return (
    <div className="p-8">
      <div className="flex justify-between items-center mb-8">
        <h1 className="text-3xl font-bold tracking-tight">Verified Records</h1>
        <div className="relative">
          <input 
            type="text" 
            placeholder="Search by Loan ID or Borrower..." 
            className="bg-[var(--card)] border border-[var(--border)] rounded-md pl-10 pr-4 py-2 w-80 text-sm focus:outline-none focus:ring-1 focus:ring-[var(--primary)]"
          />
          <span className="absolute left-3 top-2.5 text-[var(--muted-foreground)]">🔍</span>
        </div>
      </div>

      <div className="glass-panel rounded-xl overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-sm text-left">
            <thead className="text-xs text-[var(--muted-foreground)] uppercase bg-[var(--secondary)]">
              <tr>
                <th className="px-6 py-4">Loan ID</th>
                <th className="px-6 py-4">Borrower</th>
                <th className="px-6 py-4">Principal</th>
                <th className="px-6 py-4">Verified By</th>
                <th className="px-6 py-4">Hash</th>
                <th className="px-6 py-4">Action</th>
              </tr>
            </thead>
            <tbody>
              {/* Placeholder row */}
              <tr className="border-b border-[var(--border)] hover:bg-[var(--secondary)]/50 transition-colors">
                <td className="px-6 py-4 font-medium text-white">L-10023</td>
                <td className="px-6 py-4">B-9921</td>
                <td className="px-6 py-4">$15,000.00</td>
                <td className="px-6 py-4 text-[var(--primary)]">@reviewer</td>
                <td className="px-6 py-4 font-mono text-xs text-[var(--muted-foreground)]">a3f9...2c1b</td>
                <td className="px-6 py-4">
                  <button className="text-[var(--accent)] hover:text-white transition-colors">View Lineage</button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
        <div className="p-4 text-center text-[var(--muted-foreground)] text-xs border-t border-[var(--border)]">
          Cryptographic hash generation and verifiable data views will be implemented in Phase 5.
        </div>
      </div>
    </div>
  );
}
