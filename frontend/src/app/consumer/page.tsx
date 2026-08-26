"use client";
import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { apiFetch, getToken, getUserRole } from "@/lib/auth";
import { ShieldCheck, Download, Activity, FileCheck, Hash } from "lucide-react";

export default function ConsumerDashboard() {
  const router = useRouter();
  const [summary, setSummary] = useState<any>(null);
  const [verifiedLoans, setVerifiedLoans] = useState<any[]>([]);

  useEffect(() => {
    const t = getToken();
    if (!t) {
      router.push("/login");
      return;
    }
    const role = getUserRole();
    if (role !== "DATA_CONSUMER" && role !== "REVIEWER") {
      router.push("/login");
      return;
    }

    const fetchData = async () => {
      try {
        const [sumRes, loansRes] = await Promise.all([
          apiFetch("/api/summary"),
          apiFetch("/api/verified-loans")
        ]);
        
        if (sumRes.ok) setSummary(await sumRes.json());
        if (loansRes.ok) setVerifiedLoans(await loansRes.json());
      } catch (e) {
        console.error(e);
      }
    };
    fetchData();
  }, [router]);

  const handleExport = () => {
    window.location.href = "http://localhost:8000/api/verified-loans/export";
  };

  if (!summary) return <div className="p-8 text-white">Loading Dashboard...</div>;

  return (
    <div className="p-8 max-w-7xl mx-auto text-white">
      <div className="flex justify-between items-center mb-8">
        <div>
          <h1 className="text-3xl font-bold flex items-center gap-2">
            <ShieldCheck className="w-8 h-8 text-green-400" />
            Verified Data Consumer
          </h1>
          <p className="text-slate-400">Access immutable, verified loan records and trace data lineage.</p>
        </div>
        <button 
          onClick={handleExport}
          className="flex items-center gap-2 px-4 py-2 bg-slate-800 hover:bg-slate-700 border border-slate-600 rounded font-semibold text-sm transition-colors"
        >
          <Download className="w-4 h-4" /> Export Verified CSV
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
        <div className="bg-slate-900 border border-slate-700 p-5 rounded-lg shadow-lg">
          <div className="text-slate-400 text-xs font-bold uppercase tracking-wider mb-1 flex items-center gap-1">
            <Activity className="w-4 h-4" /> Data Quality Score
          </div>
          <div className="text-4xl font-mono text-blue-400">{summary.data_quality_score}%</div>
          <p className="text-xs text-slate-500 mt-2">Based on open exceptions vs total loans</p>
        </div>
        
        <div className="bg-slate-900 border border-slate-700 p-5 rounded-lg shadow-lg">
          <div className="text-slate-400 text-xs font-bold uppercase tracking-wider mb-1 flex items-center gap-1">
            <FileCheck className="w-4 h-4" /> Verified Records
          </div>
          <div className="text-4xl font-mono text-green-400">{summary.verified_records}</div>
          <p className="text-xs text-slate-500 mt-2">Immutable records on ledger</p>
        </div>

        <div className="bg-slate-900 border border-slate-700 p-5 rounded-lg shadow-lg">
          <div className="text-slate-400 text-xs font-bold uppercase tracking-wider mb-1">
            Total Normalized Loans
          </div>
          <div className="text-4xl font-mono text-slate-200">{summary.total_loans}</div>
          <p className="text-xs text-slate-500 mt-2">Processed from {summary.total_batches} batches</p>
        </div>

        <div className="bg-slate-900 border border-slate-700 p-5 rounded-lg shadow-lg">
          <div className="text-slate-400 text-xs font-bold uppercase tracking-wider mb-1">
            Open Exceptions
          </div>
          <div className="text-4xl font-mono text-orange-400">{summary.open_exceptions}</div>
          <p className="text-xs text-slate-500 mt-2">Currently in review queue</p>
        </div>
      </div>

      <div className="bg-slate-900 border border-slate-700 rounded-lg shadow-lg overflow-hidden">
        <div className="p-4 border-b border-slate-800 flex justify-between items-center bg-slate-800/50">
          <h2 className="text-lg font-semibold">Verified Ledger</h2>
          <div className="text-sm text-slate-400 font-mono">Showing {verifiedLoans.length} immutable records</div>
        </div>
        
        {verifiedLoans.length === 0 ? (
          <div className="p-10 text-center text-slate-500">
            No verified records available on the ledger.
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-sm text-left">
              <thead className="bg-slate-800/80 text-slate-400 uppercase text-xs">
                <tr>
                  <th className="px-4 py-3">Record ID</th>
                  <th className="px-4 py-3">Loan ID</th>
                  <th className="px-4 py-3">Verified On</th>
                  <th className="px-4 py-3">Balance</th>
                  <th className="px-4 py-3">Status</th>
                  <th className="px-4 py-3 text-right">SHA-256 Hash</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800">
                {verifiedLoans.map((loan) => (
                  <tr key={loan.id} className="hover:bg-slate-800/50 transition-colors">
                    <td className="px-4 py-3 font-mono">
                      <Link href={`/consumer/${loan.id}`} className="text-blue-400 hover:underline">VRF-{loan.id}-v{loan.version}</Link>
                    </td>
                    <td className="px-4 py-3 font-mono text-slate-300">{loan.loan_id}</td>
                    <td className="px-4 py-3 text-slate-400">{new Date(loan.verification_timestamp).toLocaleString()}</td>
                    <td className="px-4 py-3">${loan.canonical_data?.current_balance?.toLocaleString() || 'N/A'}</td>
                    <td className="px-4 py-3">
                      <span className="px-2 py-1 bg-green-500/20 text-green-400 rounded text-xs">Verified</span>
                    </td>
                    <td className="px-4 py-3 text-right font-mono text-xs text-slate-500 max-w-[150px] truncate" title={loan.record_hash}>
                      <div className="flex items-center justify-end gap-1">
                        <Hash className="w-3 h-3" /> {loan.record_hash.substring(0, 16)}...
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}
