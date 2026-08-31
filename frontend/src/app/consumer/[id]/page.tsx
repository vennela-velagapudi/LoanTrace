"use client";
import { useState, useEffect } from "react";
import { useParams, useRouter } from "next/navigation";
import Link from "next/link";
import { apiFetch, getToken, getUserRole } from "@/lib/auth";
import { ShieldCheck, Hash, User, Calendar, FileText, Activity } from "lucide-react";

export default function VerifiedRecordDetail() {
  const { id } = useParams();
  const router = useRouter();
  const [record, setRecord] = useState<any>(null);
  const [auditLogs, setAuditLogs] = useState<any[]>([]);

  useEffect(() => {
    const t = getToken();
    if (!t) {
      router.push("/login");
      return;
    }
    const fetchData = async () => {
      try {
        const res = await apiFetch(`/api/verified-loans/${id}`);
        if (!res.ok) {
          router.push("/consumer");
          return;
        }
        const data = await res.json();
        setRecord(data);
        
        // Fetch audit logs for this loan
        if (data.verified_data?.loan_id) {
          const auditRes = await apiFetch(`/api/audit/${data.verified_data.loan_id}`);
          if (auditRes.ok) {
            setAuditLogs(await auditRes.json());
          }
        }
      } catch (e) {
        console.error(e);
      }
    };
    fetchData();
  }, [id, router]);

  if (!record) return <div className="p-4 sm:p-8 text-slate-900">Loading verified record...</div>;

  const { verified_data, record_hash, verification_timestamp, version } = record;
  const canonical = verified_data.canonical_data || {};
  const reviewerDecisions = verified_data.reviewer_decisions || [];

  return (
    <div className="p-4 sm:p-8 max-w-6xl mx-auto text-slate-900">
      <Link href="/consumer" className="text-sm text-slate-500 hover:text-slate-900 mb-6 inline-block">← Back to Verified Ledger</Link>
      
      <div className="flex flex-col sm:flex-row justify-between items-start gap-4 sm:gap-0 mb-8">
        <div>
          <h1 className="text-3xl font-bold flex items-center gap-2">
            <ShieldCheck className="w-8 h-8 text-green-600" />
            Verified Record: VRF-{record.id}-v{version}
          </h1>
          <p className="text-slate-500 mt-1 font-mono">Loan ID: {canonical.loan_id}</p>
        </div>
        <div className="bg-white border border-slate-200 px-4 py-2 rounded flex flex-col items-start sm:items-end w-full sm:w-auto overflow-hidden break-all">
          <div className="text-xs text-slate-500 uppercase font-bold tracking-widest flex items-center gap-1">
            <Hash className="w-3 h-3" /> SHA-256 Checksum
          </div>
          <div className="font-mono text-sm text-green-600 mt-1">{record_hash}</div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        
        {/* Left Column: Canonical Data */}
        <div className="lg:col-span-2 space-y-6">
          <div className="bg-white border border-slate-200 rounded-xl overflow-hidden shadow-lg">
            <div className="p-4 border-b border-slate-200 bg-slate-50 font-semibold text-slate-900">
              Canonical Loan Data (Immutable)
            </div>
            <div className="p-4 grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-y-6 gap-x-4">
              {Object.entries(canonical).map(([key, value]) => (
                <div key={key}>
                  <p className="text-xs text-slate-500 uppercase tracking-wider mb-1 font-semibold">{key.replace(/_/g, ' ')}</p>
                  <p className="font-mono text-sm text-slate-900 bg-slate-50 p-2 rounded border border-slate-200 min-h-[36px]">
                    {value !== null ? String(value) : <span className="text-slate-600">null</span>}
                  </p>
                </div>
              ))}
            </div>
          </div>
          
          <div className="bg-white border border-slate-200 rounded-xl overflow-hidden shadow-lg">
            <div className="p-4 border-b border-slate-200 bg-slate-50 font-semibold text-slate-900">
              Reviewer Decisions & Corrections
            </div>
            <div className="p-4">
              {reviewerDecisions.length === 0 ? (
                <p className="text-sm text-slate-500 italic">No human corrections were required. Record passed all validation rules automatically.</p>
              ) : (
                <ul className="space-y-3">
                  {reviewerDecisions.map((dec: any, idx: number) => (
                    <li key={idx} className="bg-white p-3 rounded border border-slate-200 text-sm">
                      <div className="flex justify-between items-start mb-2">
                        <span className="font-mono text-indigo-600">{dec.rule}</span>
                        <span className="text-xs bg-slate-100 px-2 py-1 rounded text-slate-600">EXC-{dec.exception_id}</span>
                      </div>
                      <p className="text-slate-600"><span className="text-slate-500">Resolution:</span> {dec.reason}</p>
                    </li>
                  ))}
                </ul>
              )}
            </div>
          </div>
        </div>
        
        {/* Right Column: Lineage & Audit */}
        <div className="space-y-6">
          <div className="bg-white border border-slate-200 rounded-xl overflow-hidden shadow-lg">
            <div className="p-4 border-b border-slate-200 bg-slate-50 font-semibold text-slate-900">
              Verification Lineage
            </div>
            <div className="p-4 space-y-4 text-sm">
              <div className="flex items-center justify-between border-b border-slate-200 pb-3">
                <span className="text-slate-500 flex items-center gap-2"><Calendar className="w-4 h-4" /> Verified On</span>
                <span className="text-slate-900 font-mono text-xs">{new Date(verification_timestamp).toLocaleString()}</span>
              </div>
              <div className="flex items-center justify-between border-b border-slate-200 pb-3">
                <span className="text-slate-500 flex items-center gap-2"><User className="w-4 h-4" /> Verified By</span>
                <span className="text-slate-900 font-mono text-xs">User ID {record.verified_by}</span>
              </div>
              <div className="flex items-center justify-between border-b border-slate-200 pb-3">
                <span className="text-slate-500 flex items-center gap-2"><Activity className="w-4 h-4" /> Source Batch</span>
                <span className="text-slate-900 font-mono text-xs">BAT-{verified_data.source_batch_id}</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-slate-500 flex items-center gap-2"><FileText className="w-4 h-4" /> Raw Record</span>
                <span className="text-slate-900 font-mono text-xs">RAW-{verified_data.raw_record_id}</span>
              </div>
            </div>
          </div>

          <div className="bg-white border border-slate-200 rounded-xl overflow-hidden shadow-lg h-[400px] flex flex-col">
            <div className="p-4 border-b border-slate-200 bg-slate-50 font-semibold text-slate-900">
              Complete Audit Trail
            </div>
            <div className="p-4 overflow-y-auto flex-1">
              <div className="space-y-4 relative before:absolute before:inset-0 before:ml-2 before:-translate-x-px before:h-full before:w-0.5 before:bg-slate-100">
                {auditLogs.map((log) => (
                  <div key={log.id} className="relative flex items-start gap-4">
                    <div className={`w-4 h-4 mt-1 rounded-full border-2 shrink-0 z-10 
                      ${log.action.includes('AI_') ? 'bg-indigo-100 border-indigo-400' : 
                        log.action.includes('VERIFI') ? 'bg-green-100 border-green-400' : 
                        'bg-white border-slate-300'}`} 
                    />
                    <div className="flex-1 bg-slate-50 p-2 rounded border border-slate-200">
                      <div className="text-xs font-bold text-slate-900">{log.action}</div>
                      <div className="text-[10px] text-slate-500 mt-1">{new Date(log.timestamp).toLocaleString()} • User {log.user_id || 'System'}</div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>

      </div>
    </div>
  );
}
