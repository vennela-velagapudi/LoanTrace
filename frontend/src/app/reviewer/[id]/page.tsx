"use client";
import { useState, useEffect } from "react";
import { useParams, useRouter } from "next/navigation";
import Link from "next/link";
import { apiFetch, getToken, getUserRole } from "@/lib/auth";

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

  if (!data) return <div className="p-8">Loading...</div>;

  const { exception, loan, raw_source, comments } = data;

  return (
    <div className="p-8 max-w-7xl mx-auto grid grid-cols-1 lg:grid-cols-3 gap-8">
      {/* Left Column: Details & Editing */}
      <div className="lg:col-span-2 space-y-6">
        <div>
          <Link href="/reviewer" className="text-sm text-[var(--muted-foreground)] hover:text-[var(--primary)] mb-4 inline-block">← Back to Queue</Link>
          <div className="flex items-center gap-4 mb-2">
            <h1 className="text-2xl font-bold">Exception EXC-{exception.id}</h1>
            <span className={`px-2 py-1 rounded text-xs ${
              exception.status === 'OPEN' ? 'bg-orange-500/20 text-orange-400' :
              exception.status === 'IN_REVIEW' ? 'bg-blue-500/20 text-blue-400' :
              exception.status === 'RESOLVED' ? 'bg-green-500/20 text-green-400' :
              'bg-gray-500/20 text-gray-400'
            }`}>{exception.status}</span>
          </div>
          <p className="text-[var(--muted-foreground)]">{exception.description}</p>
        </div>

        <div className="bg-[var(--card)] border border-[var(--border)] rounded-xl overflow-hidden">
          <div className="p-4 border-b border-[var(--border)] bg-[var(--secondary)]/30 font-medium">
            Validation Failure Details
          </div>
          <div className="p-4 grid grid-cols-2 gap-4 text-sm">
            <div>
              <p className="text-[var(--muted-foreground)]">Rule Name</p>
              <p className="font-mono">{exception.rule_name}</p>
            </div>
            <div>
              <p className="text-[var(--muted-foreground)]">Severity</p>
              <p className="font-mono text-red-400">{exception.severity}</p>
            </div>
            <div>
              <p className="text-[var(--muted-foreground)]">Affected Field</p>
              <p className="font-mono">{exception.field}</p>
            </div>
            <div>
              <p className="text-[var(--muted-foreground)]">Expected Condition</p>
              <p className="font-mono text-green-400">{exception.expected_condition}</p>
            </div>
            <div className="col-span-2">
              <p className="text-[var(--muted-foreground)]">Actual Value Recorded</p>
              <p className="font-mono text-red-400">{exception.actual_value}</p>
            </div>
          </div>
        </div>

        <div className="bg-[var(--card)] border border-[var(--border)] rounded-xl overflow-hidden">
          <div className="p-4 border-b border-[var(--border)] bg-[var(--secondary)]/30 font-medium">
            Data Comparison
          </div>
          <div className="p-4 text-sm space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div className="p-3 bg-red-500/5 rounded border border-red-500/10">
                <h3 className="font-bold mb-2 text-red-400 text-xs uppercase tracking-wider">Source Value (Raw)</h3>
                <p className="font-mono">{exception.field}: {raw_source?.[exception.field] || 'null'}</p>
              </div>
              <div className="p-3 bg-blue-500/5 rounded border border-blue-500/10">
                <h3 className="font-bold mb-2 text-blue-400 text-xs uppercase tracking-wider">Canonical Value (Normalized)</h3>
                <p className="font-mono">{exception.field}: {loan?.[exception.field] || 'null'}</p>
              </div>
            </div>
          </div>
        </div>

        <div className="bg-[var(--card)] border border-[var(--border)] rounded-xl overflow-hidden">
          <div className="p-4 border-b border-[var(--border)] bg-[var(--secondary)]/30 font-medium">
            Edit Canonical Field
          </div>
          <div className="p-4 space-y-4 text-sm">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block mb-1 text-[var(--muted-foreground)]">Field</label>
                <select 
                  className="w-full bg-[var(--background)] border border-[var(--border)] rounded px-3 py-2"
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
                <label className="block mb-1 text-[var(--muted-foreground)]">New Value</label>
                <input 
                  type="text" 
                  className="w-full bg-[var(--background)] border border-[var(--border)] rounded px-3 py-2"
                  value={editValue}
                  onChange={(e) => setEditValue(e.target.value)}
                  disabled={!editField}
                />
              </div>
            </div>
            <div>
              <label className="block mb-1 text-[var(--muted-foreground)]">Reason for Edit</label>
              <input 
                type="text" 
                className="w-full bg-[var(--background)] border border-[var(--border)] rounded px-3 py-2"
                value={editReason}
                onChange={(e) => setEditReason(e.target.value)}
                disabled={!editField}
              />
            </div>
            <button 
              className="px-4 py-2 bg-[var(--primary)] text-white rounded disabled:opacity-50"
              disabled={!editField || !editReason}
              onClick={() => handleAction('/fields', 'PATCH', { field_name: editField, new_value: editValue, reason: editReason })}
            >
              Save Edit & Re-validate
            </button>
          </div>
        </div>
      </div>

      {/* Right Column: Actions & Timeline */}
      <div className="space-y-6">
        <div className="bg-[var(--card)] border border-[var(--border)] rounded-xl overflow-hidden">
          <div className="p-4 border-b border-[var(--border)] bg-[var(--secondary)]/30 font-medium">
            Review Actions
          </div>
          <div className="p-4 space-y-3 text-sm">
            {exception.status === "OPEN" && (
              <button 
                className="w-full py-2 bg-blue-600 hover:bg-blue-700 text-white rounded"
                onClick={() => handleAction('/assign', 'PATCH', { user_id: 2 })}
              >
                Assign to Me & Start Review
              </button>
            )}
            
            <textarea
              className="w-full bg-[var(--background)] border border-[var(--border)] rounded px-3 py-2 h-20"
              placeholder="Decision reason..."
              value={decisionReason}
              onChange={e => setDecisionReason(e.target.value)}
            />
            
            <div className="grid grid-cols-2 gap-2">
              <button 
                className="py-2 bg-green-600 hover:bg-green-700 text-white rounded disabled:opacity-50"
                disabled={!decisionReason}
                onClick={() => handleAction('/decision', 'POST', { decision: "APPROVE", reason: decisionReason })}
              >
                Approve
              </button>
              <button 
                className="py-2 bg-red-600 hover:bg-red-700 text-white rounded disabled:opacity-50"
                disabled={!decisionReason}
                onClick={() => handleAction('/decision', 'POST', { decision: "REJECT", reason: decisionReason })}
              >
                Reject
              </button>
            </div>
            <button 
              className="w-full py-2 bg-orange-600 hover:bg-orange-700 text-white rounded disabled:opacity-50"
              disabled={!decisionReason}
              onClick={() => handleAction('/decision', 'POST', { decision: "REQUEST_CORRECTION", reason: decisionReason })}
            >
              Request Correction
            </button>
          </div>
        </div>

        <div className="bg-[var(--card)] border border-[var(--border)] rounded-xl overflow-hidden">
          <div className="p-4 border-b border-[var(--border)] bg-[var(--secondary)]/30 font-medium">
            Comments
          </div>
          <div className="p-4 space-y-4">
            <div className="space-y-3 max-h-40 overflow-y-auto">
              {comments.map((c: any) => (
                <div key={c.id} className="text-xs bg-[var(--secondary)]/20 p-2 rounded">
                  <p className="font-semibold">{new Date(c.created_at).toLocaleString()}</p>
                  <p>{c.comment_text}</p>
                </div>
              ))}
            </div>
            <div className="flex gap-2">
              <input 
                type="text" 
                className="flex-1 text-sm bg-[var(--background)] border border-[var(--border)] rounded px-2"
                placeholder="Add comment..."
                value={newComment}
                onChange={e => setNewComment(e.target.value)}
              />
              <button 
                className="px-3 py-1 bg-[var(--secondary)] rounded text-sm hover:bg-[var(--border)]"
                onClick={() => handleAction('/comments', 'POST', { text: newComment })}
              >
                Post
              </button>
            </div>
          </div>
        </div>

        <div className="bg-[var(--card)] border border-[var(--border)] rounded-xl overflow-hidden">
          <div className="p-4 border-b border-[var(--border)] bg-[var(--secondary)]/30 font-medium">
            Audit Timeline
          </div>
          <div className="p-4">
            <div className="space-y-4 relative before:absolute before:inset-0 before:ml-2 before:-translate-x-px md:before:mx-auto md:before:translate-x-0 before:h-full before:w-0.5 before:bg-gradient-to-b before:from-transparent before:via-[var(--border)] before:to-transparent">
              {auditLogs.map((log, i) => (
                <div key={log.id} className="relative flex items-center justify-between md:justify-normal md:odd:flex-row-reverse group is-active text-xs">
                  <div className="flex items-center justify-center w-4 h-4 rounded-full border border-white bg-slate-300 group-[.is-active]:bg-[var(--primary)] shrink-0 md:order-1 md:group-odd:-translate-x-1/2 md:group-even:translate-x-1/2 shadow" />
                  <div className="w-[calc(100%-2rem)] md:w-[calc(50%-1.5rem)] p-2 rounded border border-[var(--border)] bg-[var(--secondary)]/10">
                    <div className="font-bold text-[var(--foreground)]">{log.action}</div>
                    <div className="text-[var(--muted-foreground)]">{new Date(log.timestamp).toLocaleTimeString()}</div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

      </div>
    </div>
  );
}
