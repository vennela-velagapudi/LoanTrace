"use client";
import { useState, useEffect } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { apiFetch, getToken, getUserRole } from "@/lib/auth";

export default function ReviewerDashboard() {
  const [exceptions, setExceptions] = useState<any[]>([]);
  const [filterStatus, setFilterStatus] = useState<string>("ALL");
  const [summary, setSummary] = useState<any>(null);
  const [token, setToken] = useState<string>("");

  const router = useRouter();

  useEffect(() => {
    const t = getToken();
    if (!t) {
      router.push("/login");
      return;
    }
    const role = getUserRole();
    if (role !== "REVIEWER") {
      router.push("/login"); // or forbidden page
      return;
    }
    setToken(t);
    fetchData();
  }, [router]);

  const [searchLoanId, setSearchLoanId] = useState<string>("");
  const [searchBorrowerId, setSearchBorrowerId] = useState<string>("");

  const fetchData = async () => {
    try {
      const sumRes = await apiFetch("/api/summary");
      if (sumRes.ok) setSummary(await sumRes.json());
      
      let query = "/api/exceptions?limit=10000";
      if (searchLoanId) query += `&loan_id=${searchLoanId}`;
      if (searchBorrowerId) query += `&borrower_id=${searchBorrowerId}`;

      const excRes = await apiFetch(query);
      if (excRes.ok) setExceptions(await excRes.json());
    } catch (e) {
      console.error(e);
    }
  };

  return (
    <div className="p-4 sm:p-8 max-w-7xl mx-auto">
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 sm:gap-0 mb-4 sm:mb-6">
        <div>
          <h1 className="text-3xl font-bold">Reviewer Dashboard</h1>
          <p className="text-[var(--muted-foreground)]">Manage and resolve validation exceptions</p>
        </div>
        <Link href="/reviewer/ai-tools" className="px-4 py-2 bg-purple-600 hover:bg-purple-700 text-white rounded font-semibold shadow flex items-center gap-2">
          AI Tools Workspace
        </Link>
      </div>

      {summary && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
          <div 
            onClick={() => setFilterStatus("ALL")}
            className={`bg-[var(--card)] border rounded-xl p-4 shadow-sm cursor-pointer transition-all ${filterStatus === 'ALL' ? 'ring-2 ring-slate-400 border-transparent' : 'border-[var(--border)] hover:border-slate-400'}`}
          >
            <h3 className="text-sm font-medium text-[var(--muted-foreground)] mb-1">Total Exceptions</h3>
            <p className="text-3xl font-bold">{summary.total_validation_failures}</p>
          </div>
          <div 
            onClick={() => setFilterStatus("OPEN")}
            className={`bg-[var(--card)] border rounded-xl p-4 shadow-sm cursor-pointer transition-all ${filterStatus === 'OPEN' ? 'ring-2 ring-orange-500 border-transparent' : 'border-[var(--border)] hover:border-orange-300'}`}
          >
            <h3 className="text-sm font-medium text-[var(--muted-foreground)] mb-1">Open</h3>
            <p className="text-3xl font-bold text-orange-600">
  		{summary.open_exceptions}
	    </p>
          </div>
          <div 
            onClick={() => setFilterStatus("IN_REVIEW")}
            className={`bg-[var(--card)] border rounded-xl p-4 shadow-sm cursor-pointer transition-all ${filterStatus === 'IN_REVIEW' ? 'ring-2 ring-blue-500 border-transparent' : 'border-[var(--border)] hover:border-blue-300'}`}
          >
            <h3 className="text-sm font-medium text-[var(--muted-foreground)] mb-1">In Review</h3>
            <p className="text-3xl font-bold text-blue-600">
              {exceptions.filter(e => e.status === "IN_REVIEW").length}
            </p>
          </div>
          <div 
            onClick={() => setFilterStatus("RESOLVED")}
            className={`bg-[var(--card)] border rounded-xl p-4 shadow-sm cursor-pointer transition-all ${filterStatus === 'RESOLVED' ? 'ring-2 ring-green-500 border-transparent' : 'border-[var(--border)] hover:border-green-300'}`}
          >
            <h3 className="text-sm font-medium text-[var(--muted-foreground)] mb-1">Resolved</h3>
            <p className="text-3xl font-bold text-green-600">
  		{summary.resolved_exceptions}
	    </p>
          </div>
        </div>
      )}

      <div className="bg-[var(--card)] border border-[var(--border)] rounded-xl shadow-sm overflow-hidden">
        <div className="p-4 border-b border-[var(--border)] flex flex-col sm:flex-row justify-between items-start sm:items-center bg-[var(--secondary)]/30 gap-4">
          <h2 className="font-semibold">Exception Queue</h2>
          <div className="flex gap-2">
            <input 
              type="text" 
              placeholder="Loan ID" 
              value={searchLoanId} 
              onChange={(e) => setSearchLoanId(e.target.value)}
              className="px-3 py-1.5 text-sm border border-[var(--border)] rounded bg-[var(--background)]"
            />
            <input 
              type="text" 
              placeholder="Borrower ID" 
              value={searchBorrowerId} 
              onChange={(e) => setSearchBorrowerId(e.target.value)}
              className="px-3 py-1.5 text-sm border border-[var(--border)] rounded bg-[var(--background)]"
            />
            <button 
              onClick={fetchData}
              className="px-3 py-1.5 bg-blue-600 hover:bg-blue-700 text-white rounded text-sm font-medium"
            >
              Search
            </button>
          </div>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-sm text-left">
            <thead className="text-xs text-[var(--muted-foreground)] uppercase bg-[var(--secondary)]/50 border-b border-[var(--border)]">
              <tr>
                <th className="px-4 py-3">ID</th>
                <th className="px-4 py-3">Loan ID</th>
                <th className="px-4 py-3">Rule Name</th>
                <th className="px-4 py-3">Severity</th>
                <th className="px-4 py-3">Status</th>
                <th className="px-4 py-3">Created</th>
                <th className="px-4 py-3 text-right">Action</th>
              </tr>
            </thead>
            <tbody>
              {exceptions.filter(e => filterStatus === "ALL" || e.status === filterStatus).map(exc => (
                <tr key={exc.id} className="border-b border-[var(--border)] hover:bg-[var(--secondary)]/20 transition-colors">
                  <td className="px-4 py-3 font-medium">EXC-{exc.id}</td>
                  <td className="px-4 py-3 font-mono text-xs">{exc.normalized_loan_id}</td>
                  <td className="px-4 py-3">{exc.rule_name}</td>
                  <td className="px-4 py-3">
                    <span className={`px-2 py-1 rounded text-xs font-medium ${
                      exc.severity === 'CRITICAL' ? 'bg-red-100 text-red-700' : 
                      exc.severity === 'HIGH' ? 'bg-orange-100 text-orange-700' : 
                      'bg-yellow-100 text-yellow-700'
                    }`}>
                      {exc.severity}
                    </span>
                  </td>
                  <td className="px-4 py-3">
                    <span className="px-2 py-1 bg-[var(--secondary)] rounded text-xs font-medium">{exc.status}</span>
                  </td>
                  <td className="px-4 py-3 text-[var(--muted-foreground)]">
                    {new Date(exc.created_at).toLocaleDateString()}
                  </td>
                  <td className="px-4 py-3 text-right">
                    <Link href={`/reviewer/${exc.id}`} className="text-[var(--primary)] hover:underline font-medium text-xs">
                      Review &rarr;
                    </Link>
                  </td>
                </tr>
              ))}
              {exceptions.filter(e => filterStatus === "ALL" || e.status === filterStatus).length === 0 && (
                <tr>
                  <td colSpan={7} className="px-4 py-8 text-center text-[var(--muted-foreground)]">
                    No exceptions found.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
