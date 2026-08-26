"use client";
import { useState, useEffect } from "react";
import { useParams, useRouter } from "next/navigation";
import Link from "next/link";
import { apiFetch, getToken, getUserRole } from "@/lib/auth";
import AIAssistantPanel from "@/components/AIAssistantPanel";

const EDITABLE_FIELDS = [
    "current_balance",
    "interest_rate",
    "payment_status",
    "days_past_due",
    "servicer_name",
    "document_status",
    "borrower_state",
    "last_payment_date"
];

export default function ExceptionDetail() {
  const { id } = useParams();
  const router = useRouter();
  const [data, setData] = useState<any>(null);
  const [auditLogs, setAuditLogs] = useState<any[]>([]);
  const [editField, setEditField] = useState<string>("");
  const [editValue, setEditValue] = useState<string>("");
  const [editReason, setEditReason] = useState<string>("");
  
  // Comment state
  const [newComment, setNewComment] = useState<string>("");
  const [decisionReason, setDecisionReason] = useState<string>("");

  const fetchData = async () => {
    try {
      const res = await apiFetch(`/api/exceptions/${id}`);
      if (!res.ok) return;
      const d = await res.json();
      setData(d);
      
      if (d.loan?.loan_id) {
        const auditRes = await apiFetch(`/api/audit/${d.loan.loan_id}`);
        if (auditRes.ok) setAuditLogs(await auditRes.json());
      }
    } catch (e) {
      console.error(e);
    }
  };

  useEffect(() => {
    const t = getToken();
    if (!t) {
      router.push("/login");
      return;
    }
    if (getUserRole() !== "REVIEWER") {
      router.push("/login");
      return;
    }
    fetchData();
  }, [id, router]);

  const handleAction = async (endpoint: string, method: string, body: any) => {
    try {
      const res = await apiFetch(`/api/exceptions/${id}${endpoint}`, {
        method,
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body)
      });
      if (res.ok) {
        fetchData();
        if (endpoint === '/fields') {
          setEditField(""); setEditValue(""); setEditReason("");
        }
        if (endpoint === '/comments') {
          setNewComment("");
        }
      }
    } catch(e) {
      console.error(e);
    }
  };

  if (!data) return <div className="p-8 text-white">Loading...</div>;

  const { exception, loan, raw_source, comments } = data;

  return (
    <div className="p-8 max-w-[1400px] mx-auto">
      <Link href="/reviewer" className="text-sm text-slate-400 hover:text-white mb-6 inline-block">← Back to Queue</Link>
      
      <div className="flex items-center gap-4 mb-6">
        <h1 className="text-3xl font-bold text-white">Exception EXC-{exception.id}</h1>
        <span className={`px-3 py-1 rounded text-sm font-semibold ${
          exception.status === 'OPEN' ? 'bg-orange-500/20 text-orange-400 border border-orange-500/30' :
          exception.status === 'IN_REVIEW' ? 'bg-blue-500/20 text-blue-400 border border-blue-500/30' :
          exception.status === 'RESOLVED' ? 'bg-green-500/20 text-green-400 border border-green-500/30' :
          'bg-gray-500/20 text-gray-400 border border-gray-500/30'
        }`}>{exception.status}</span>
      </div>

      <div className="grid grid-cols-1 xl:grid-cols-2 gap-8 h-[800px]">
        {/* Left Column: Human Details & Editing */}
        <div className="space-y-6 overflow-y-auto pr-2 h-full">
          
          <div className="bg-slate-900 border border-slate-700 rounded-xl overflow-hidden shadow-lg">
            <div className="p-4 border-b border-slate-800 bg-slate-800/50 font-semibold text-slate-200">
              Validation Failure Details
            </div>
            <div className="p-4 grid grid-cols-2 gap-4 text-sm text-slate-300">
              <div className="col-span-2">
                <p className="text-slate-400 mb-1">Description</p>
                <p className="text-white">{exception.description}</p>
              </div>
              <div>
                <p className="text-slate-400">Rule Name</p>
                <p className="font-mono text-purple-400">{exception.rule_name}</p>
              </div>
              <div>
                <p className="text-slate-400">System Severity</p>
                <p className="font-mono text-red-400">{exception.severity}</p>
              </div>
              <div>
                <p className="text-slate-400">Affected Field</p>
                <p className="font-mono text-blue-400">{exception.field}</p>
              </div>
              <div>
                <p className="text-slate-400">Expected Condition</p>
                <p className="font-mono text-green-400">{exception.expected_condition}</p>
              </div>
              <div className="col-span-2 p-3 bg-red-900/20 rounded border border-red-900/50">
                <p className="text-slate-400 mb-1">Actual Value Recorded</p>
                <p className="font-mono text-red-400 font-bold">{exception.actual_value}</p>
              </div>
            </div>
          </div>

          <div className="bg-slate-900 border border-slate-700 rounded-xl overflow-hidden shadow-lg">
            <div className="p-4 border-b border-slate-800 bg-slate-800/50 font-semibold text-slate-200">
              Data Comparison
            </div>
            <div className="p-4 text-sm space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div className="p-3 bg-slate-800 rounded border border-slate-700">
                  <h3 className="font-bold mb-2 text-slate-400 text-xs uppercase tracking-wider">Source Value (Loan Tape)</h3>
                  <p className="font-mono text-slate-200">{exception.field}: {raw_source?.[exception.field] || 'null'}</p>
                </div>
                <div className="p-3 bg-blue-900/20 rounded border border-blue-900/50">
                  <h3 className="font-bold mb-2 text-blue-400 text-xs uppercase tracking-wider">Canonical Value (Normalized)</h3>
                  <p className="font-mono text-slate-200">{exception.field}: {loan?.[exception.field] || 'null'}</p>
                </div>
              </div>
            </div>
          </div>

          <div className="bg-slate-900 border border-slate-700 rounded-xl overflow-hidden shadow-lg">
            <div className="p-4 border-b border-slate-800 bg-slate-800/50 font-semibold text-slate-200">
              Edit Canonical Field (Human Decision)
            </div>
            <div className="p-4 space-y-4 text-sm text-slate-300">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block mb-1 text-slate-400">Field</label>
                  <select 
                    className="w-full bg-slate-800 border border-slate-600 rounded px-3 py-2 text-white"
                    value={editField}
                    onChange={(e) => {
                      setEditField(e.target.value);
                      setEditValue(loan?.[e.target.value] || "");
                    }}
                  >
                    <option value="">Select an editable field...</option>
                    {EDITABLE_FIELDS.map(f => <option key={f} value={f}>{f}</option>)}
                  </select>
                </div>
                <div>
                  <label className="block mb-1 text-slate-400">New Value</label>
                  <input 
                    type="text" 
                    className="w-full bg-slate-800 border border-slate-600 rounded px-3 py-2 text-white"
                    value={editValue}
                    onChange={(e) => setEditValue(e.target.value)}
                    disabled={!editField}
                  />
                </div>
              </div>
              <div>
                <label className="block mb-1 text-slate-400">Reason for Edit</label>
                <input 
                  type="text" 
                  className="w-full bg-slate-800 border border-slate-600 rounded px-3 py-2 text-white"
                  value={editReason}
                  onChange={(e) => setEditReason(e.target.value)}
                  disabled={!editField}
                />
              </div>
              <button 
                className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white font-semibold rounded disabled:opacity-50"
                disabled={!editField || !editReason}
                onClick={() => handleAction('/fields', 'PATCH', { field_name: editField, new_value: editValue, reason: editReason })}
              >
                Save Edit & Re-validate
              </button>
            </div>
          </div>

          <div className="bg-slate-900 border border-slate-700 rounded-xl overflow-hidden shadow-lg border-l-4 border-l-purple-500">
            <div className="p-4 border-b border-slate-800 bg-slate-800/50 font-semibold text-slate-200">
              Final Review Action (Human Decision)
            </div>
            <div className="p-4 space-y-3 text-sm">
              {exception.status === "OPEN" && (
                <button 
                  className="w-full py-2 bg-slate-700 hover:bg-slate-600 text-white rounded mb-4"
                  onClick={() => handleAction('/assign', 'PATCH', { user_id: 2 })}
                >
                  Assign to Me & Start Review
                </button>
              )}
              
              <textarea
                className="w-full bg-slate-800 border border-slate-600 rounded px-3 py-2 h-20 text-white"
                placeholder="Decision reason..."
                value={decisionReason}
                onChange={e => setDecisionReason(e.target.value)}
              />
              
              <div className="grid grid-cols-2 gap-3 mt-3">
                <button 
                  className="py-2 bg-green-600 hover:bg-green-700 text-white font-semibold rounded shadow disabled:opacity-50"
                  disabled={!decisionReason}
                  onClick={() => handleAction('/decision', 'POST', { decision: "APPROVE", reason: decisionReason })}
                >
                  Approve Exception
                </button>
                <button 
                  className="py-2 bg-red-600 hover:bg-red-700 text-white font-semibold rounded shadow disabled:opacity-50"
                  disabled={!decisionReason}
                  onClick={() => handleAction('/decision', 'POST', { decision: "REJECT", reason: decisionReason })}
                >
                  Reject Exception
                </button>
              </div>
              <button 
                className="w-full mt-3 py-2 bg-orange-600 hover:bg-orange-700 text-white font-semibold rounded shadow disabled:opacity-50"
                disabled={!decisionReason}
                onClick={() => handleAction('/decision', 'POST', { decision: "REQUEST_CORRECTION", reason: decisionReason })}
              >
                Request Correction
              </button>
            </div>
          </div>

        </div>

        {/* Right Column: AI Assistant & Timeline */}
        <div className="space-y-6 h-full flex flex-col">
          <div className="flex-1">
            <AIAssistantPanel exception={exception} onRefresh={fetchData} />
          </div>

          <div className="bg-slate-900 border border-slate-700 rounded-xl overflow-hidden shadow-lg h-64 flex flex-col">
            <div className="p-3 border-b border-slate-800 bg-slate-800/50 font-semibold text-slate-200">
              Audit Timeline & Comments
            </div>
            <div className="p-3 overflow-y-auto flex-1 text-sm text-slate-300">
              <div className="space-y-4 relative before:absolute before:inset-0 before:ml-2 before:-translate-x-px md:before:mx-auto md:before:translate-x-0 before:h-full before:w-0.5 before:bg-gradient-to-b before:from-transparent before:via-slate-700 before:to-transparent">
                {auditLogs.map((log, i) => (
                  <div key={log.id} className="relative flex items-center justify-between md:justify-normal md:odd:flex-row-reverse group is-active text-xs">
                    <div className="flex items-center justify-center w-3 h-3 rounded-full border border-slate-500 bg-slate-700 group-[.is-active]:bg-purple-500 shrink-0 md:order-1 md:group-odd:-translate-x-1/2 md:group-even:translate-x-1/2 shadow" />
                    <div className="w-[calc(100%-2rem)] md:w-[calc(50%-1.5rem)] p-2 rounded border border-slate-700 bg-slate-800/50">
                      <div className="font-bold text-slate-200">{log.action}</div>
                      <div className="text-slate-500">{new Date(log.timestamp).toLocaleTimeString()}</div>
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
