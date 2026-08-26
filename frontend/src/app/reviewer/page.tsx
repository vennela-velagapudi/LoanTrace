"use client";
import { useState, useEffect } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { apiFetch, getToken, getUserRole } from "@/lib/auth";

export default function ReviewerDashboard() {
  const [exceptions, setExceptions] = useState<any[]>([]);
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

  const fetchData = async () => {
    try {
      const sumRes = await apiFetch("/api/summary");
      if (sumRes.ok) setSummary(await sumRes.json());
      
      const excRes = await apiFetch("/api/exceptions");
      if (excRes.ok) setExceptions(await excRes.json());
    } catch (e) {
      console.error(e);
    }
  };

  return (
    <div className="p-8 max-w-7xl mx-auto">
      <div className="flex justify-between items-center mb-6">
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
          <div className="bg-[var(--card)] border border-[var(--border)] rounded-xl p-4 shadow-sm">
            <h3 className="text-sm font-medium text-[var(--muted-foreground)] mb-1">Total Exceptions</h3>
            <p className="text-3xl font-bold">{summary.total_validation_failures}</p>
          </div>
          <div className="bg-[var(--card)] border border-[var(--border)] rounded-xl p-4 shadow-sm">
            <h3 className="text-sm font-medium text-[var(--muted-foreground)] mb-1">Open</h3>
            <p className="text-3xl font-bold text-orange-400">
              {exceptions.filter(e => e.status === "OPEN").length}
            </p>
          </div>
          <div className="bg-[var(--card)] border border-[var(--border)] rounded-xl p-4 shadow-sm">
            <h3 className="text-sm font-medium text-[var(--muted-foreground)] mb-1">In Review</h3>
            <p className="text-3xl font-bold text-blue-400">
              {exceptions.filter(e => e.status === "IN_REVIEW").length}
            </p>
          </div>
          <div className="bg-[var(--card)] border border-[var(--border)] rounded-xl p-4 shadow-sm">
            <h3 className="text-sm font-medium text-[var(--muted-foreground)] mb-1">Resolved</h3>
            <p className="text-3xl font-bold text-green-400">
              {exceptions.filter(e => e.status === "RESOLVED").length}
            </p>
          </div>
        </div>
      )}

      <div className="bg-[var(--card)] border border-[var(--border)] rounded-xl shadow-sm overflow-hidden">
        <div className="p-4 border-b border-[var(--border)] flex justify-between items-center bg-[var(--secondary)]/30">
          <h2 className="font-semibold">Exception Queue</h2>
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
              {exceptions.map(exc => (
                <tr key={exc.id} className="border-b border-[var(--border)] hover:bg-[var(--secondary)]/20 transition-colors">
                  <td className="px-4 py-3 font-medium">EXC-{exc.id}</td>
                  <td className="px-4 py-3 font-mono">{exc.normalized_loan_id}</td>
                  <td className="px-4 py-3">{exc.rule_name}</td>
                  <td className="px-4 py-3">
                    <span className={`px-2 py-1 rounded text-xs ${
                      exc.severity === 'CRITICAL' ? 'bg-red-500/20 text-red-400' : 
                      exc.severity === 'HIGH' ? 'bg-orange-500/20 text-orange-400' : 
                      'bg-yellow-500/20 text-yellow-400'
                    }`}>
                      {exc.severity}
                    </span>
                  </td>
                  <td className="px-4 py-3">
                    <span className="px-2 py-1 bg-[var(--secondary)] rounded text-xs">{exc.status}</span>
                  </td>
                  <td className="px-4 py-3 text-[var(--muted-foreground)]">
                    {new Date(exc.created_at).toLocaleDateString()}
                  </td>
                  <td className="px-4 py-3 text-right">
                    <Link href={`/reviewer/${exc.id}`} className="text-[var(--primary)] hover:underline font-medium text-xs">
                      Review →
                    </Link>
                  </td>
                </tr>
              ))}
              {exceptions.length === 0 && (
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
