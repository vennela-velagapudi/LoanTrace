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

  const handleExport = async () => {
    try {
      const res = await apiFetch("/api/verified-loans/export");
      if (!res.ok) {
        console.error("Export failed:", await res.text());
        return;
      }
      
      const blob = await res.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.style.display = "none";
      a.href = url;
      a.download = "verified_loans.csv";
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    } catch (e) {
      console.error(e);
    }
  };

  if (!summary) return <div className="p-4 sm:p-8 text-slate-900">Loading Dashboard...</div>;

  return (
    <div className="p-4 sm:p-8 max-w-7xl mx-auto text-slate-900">
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 sm:gap-0 mb-6 sm:mb-8">
        <div>
          <h1 className="text-3xl font-bold flex items-center gap-2">
            <ShieldCheck className="w-8 h-8 text-green-600" />
            Verified Data Consumer
          </h1>
          <p className="text-slate-500">Access immutable, verified loan records and trace data lineage.</p>
        </div>
        <button 
          onClick={handleExport}
          className="flex items-center gap-2 px-4 py-2 bg-slate-100 hover:bg-slate-200 text-slate-800 border border-slate-300 rounded font-semibold text-sm transition-colors"
        >
          <Download className="w-4 h-4" /> Export Verified CSV
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
        <div className="bg-white border border-slate-200 p-5 rounded-lg shadow-lg">
          <div className="text-slate-500 text-xs font-bold uppercase tracking-wider mb-1 flex items-center gap-1">
            <Activity className="w-4 h-4" /> Data Quality Score
          </div>
          <div className="text-4xl font-mono text-blue-600">{summary.data_quality_score}%</div>
          <p className="text-xs text-slate-500 mt-2">Based on open exceptions vs total loans</p>
        </div>
        
        <div className="bg-white border border-slate-200 p-5 rounded-lg shadow-lg">
          <div className="text-slate-500 text-xs font-bold uppercase tracking-wider mb-1 flex items-center gap-1">
            <FileCheck className="w-4 h-4" /> Verified Records
          </div>
          <div className="text-4xl font-mono text-green-600">{summary.verified_records}</div>
          <p className="text-xs text-slate-500 mt-2">Immutable records on ledger</p>
        </div>

        <div className="bg-white border border-slate-200 p-5 rounded-lg shadow-lg">
          <div className="text-slate-500 text-xs font-bold uppercase tracking-wider mb-1">
            Total Normalized Loans
          </div>
          <div className="text-4xl font-mono text-slate-900">{summary.total_loans}</div>
          <p className="text-xs text-slate-500 mt-2">Processed from {summary.total_batches} batches</p>
        </div>

        <div className="bg-white border border-slate-200 p-5 rounded-lg shadow-lg">
          <div className="text-slate-500 text-xs font-bold uppercase tracking-wider mb-1">
            Open Exceptions
          </div>
          <div className="text-4xl font-mono text-orange-600">{summary.open_exceptions}</div>
          <p className="text-xs text-slate-500 mt-2">Currently in review queue</p>
        </div>
      </div>

      <div className="bg-white border border-slate-200 rounded-lg shadow-lg overflow-hidden">
        <div className="p-4 border-b border-slate-200 flex justify-between items-center bg-slate-50">
          <h2 className="text-lg font-semibold">Verified Ledger</h2>
          <div className="text-sm text-slate-500 font-mono">Showing {verifiedLoans.length} immutable records</div>
        </div>
        
        {verifiedLoans.length === 0 ? (
          <div className="p-10 text-center text-slate-500">
            No verified records available on the ledger.
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-sm text-left">
              <thead className="bg-slate-50 text-slate-500 uppercase text-xs">
                <tr>
                  <th className="px-4 py-3">Record ID</th>
                  <th className="px-4 py-3">Loan ID</th>
                  <th className="px-4 py-3">Verified On</th>
                  <th className="px-4 py-3">Balance</th>
                  <th className="px-4 py-3">Status</th>
                  <th className="px-4 py-3 text-right">SHA-256 Hash</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-200">
                {verifiedLoans.map((loan) => (
                  <tr key={loan.id} className="hover:bg-slate-50 transition-colors">
                    <td className="px-4 py-3 font-mono">
                      <Link href={`/consumer/${loan.id}`} className="text-blue-600 hover:underline">VRF-{loan.id}-v{loan.version}</Link>
                    </td>
                    <td className="px-4 py-3 font-mono text-slate-600">{loan.loan_id}</td>
                    <td className="px-4 py-3 text-slate-500">{new Date(loan.verification_timestamp).toLocaleString()}</td>
                    <td className="px-4 py-3">${loan.canonical_data?.current_balance?.toLocaleString() || 'N/A'}</td>
                    <td className="px-4 py-3">
                      <span className="px-2 py-1 bg-green-100 text-green-700 rounded text-xs">Verified</span>
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
