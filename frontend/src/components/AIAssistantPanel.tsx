"use client";
import { useState } from "react";
import { Bot, RefreshCcw, FileSignature, AlertCircle, Edit, Check, X, ShieldAlert } from "lucide-react";
import { apiFetch } from "@/lib/auth";

export default function AIAssistantPanel({ exception, onRefresh }: { exception: any, onRefresh: () => void }) {
  const [loading, setLoading] = useState(false);
  const [activeTab, setActiveTab] = useState("EXPLAIN");
  const [result, setResult] = useState<any>(null);
  const [editedValue, setEditedValue] = useState("");
  const [error, setError] = useState<string | null>(null);

  const invokeAI = async (action: string) => {
    setLoading(true);
    setResult(null);
    setError(null);
    setEditedValue("");
    setActiveTab(action);
    
    let endpoint = "";
    if (action === "EXPLAIN") endpoint = `/api/ai/exceptions/${exception.id}/explain`;
    if (action === "SUGGEST") endpoint = `/api/ai/exceptions/${exception.id}/suggest`;
    if (action === "COMPARE") endpoint = `/api/ai/exceptions/${exception.id}/compare`;
    if (action === "NOTE") endpoint = `/api/ai/exceptions/${exception.id}/note`;
    
    try {
      const res = await apiFetch(endpoint, { method: "POST" });
      if (!res.ok) throw new Error("AI request failed");
      const data = await res.json();
      setResult(data);
      if (action === "SUGGEST" && data.data.suggested_value) {
        setEditedValue(data.data.suggested_value);
      }
      if (action === "COMPARE" && data.data.recommended_value) {
        setEditedValue(data.data.recommended_value);
      }
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleAction = async (status: string) => {
    if (!result?.recommendation_id) return;
    setLoading(true);
    try {
      const res = await apiFetch(`/api/ai/recommendations/${result.recommendation_id}/action`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ action: status, edited_value: editedValue })
      });
      if (res.ok && status !== "REJECT") {
        alert(`Recommendation ${status} saved to audit log. You must still apply changes in the human decision panel manually.`);
      }
      setResult(null);
      onRefresh();
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="bg-slate-800 rounded-lg p-6 border border-slate-700 h-full flex flex-col">
      <div className="flex items-center space-x-2 mb-6 border-b border-slate-700 pb-4">
        <Bot className="text-purple-400 w-6 h-6" />
        <h2 className="text-xl font-semibold text-white">AI Review Assistant</h2>
        <span className="bg-purple-500/20 text-purple-300 text-xs px-2 py-1 rounded">gemini-2.5-flash</span>
      </div>

      <div className="flex flex-wrap gap-2 mb-6">
        <button onClick={() => invokeAI("EXPLAIN")} className={`px-3 py-1.5 rounded text-sm flex items-center space-x-1 ${activeTab === 'EXPLAIN' ? 'bg-purple-600 text-white' : 'bg-slate-700 text-slate-300 hover:bg-slate-600'}`}>
          <AlertCircle className="w-4 h-4" /> <span>Explain</span>
        </button>
        <button onClick={() => invokeAI("SUGGEST")} className={`px-3 py-1.5 rounded text-sm flex items-center space-x-1 ${activeTab === 'SUGGEST' ? 'bg-purple-600 text-white' : 'bg-slate-700 text-slate-300 hover:bg-slate-600'}`}>
          <RefreshCcw className="w-4 h-4" /> <span>Suggest</span>
        </button>
        <button onClick={() => invokeAI("COMPARE")} className={`px-3 py-1.5 rounded text-sm flex items-center space-x-1 ${activeTab === 'COMPARE' ? 'bg-purple-600 text-white' : 'bg-slate-700 text-slate-300 hover:bg-slate-600'}`}>
          <ShieldAlert className="w-4 h-4" /> <span>Compare Sources</span>
        </button>
        <button onClick={() => invokeAI("NOTE")} className={`px-3 py-1.5 rounded text-sm flex items-center space-x-1 ${activeTab === 'NOTE' ? 'bg-purple-600 text-white' : 'bg-slate-700 text-slate-300 hover:bg-slate-600'}`}>
          <FileSignature className="w-4 h-4" /> <span>Gen Note</span>
        </button>
      </div>

      <div className="flex-1 bg-slate-900 rounded p-4 overflow-y-auto border border-slate-700">
        {loading && (
          <div className="flex flex-col justify-center items-center h-full text-slate-400 space-y-3">
            <Bot className="w-8 h-8 animate-pulse text-purple-400" />
            <p>Analyzing exception context...</p>
          </div>
        )}
        {error && (
          <div className="text-red-400">{error}</div>
        )}
        {!loading && !error && !result && (
          <div className="text-slate-500 text-center mt-10">Select an AI action above to begin.</div>
        )}
        {!loading && result && (
          <div className="space-y-4">
            {/* Display Explain */}
            {activeTab === "EXPLAIN" && (
              <>
                <div>
                  <h4 className="text-slate-400 text-xs font-semibold uppercase">Explanation</h4>
                  <p className="text-slate-200 mt-1">{result.data.explanation}</p>
                </div>
                <div className="flex space-x-4 mt-4">
                  <div>
                    <h4 className="text-slate-400 text-xs font-semibold uppercase">AI Severity</h4>
                    <span className="text-red-400 font-bold">{result.data.severity}</span>
                  </div>
                  <div>
                    <h4 className="text-slate-400 text-xs font-semibold uppercase">Confidence</h4>
                    <span className="text-blue-400">{result.data.confidence}</span>
                  </div>
                </div>
              </>
            )}

            {/* Display Suggestion / Compare */}
            {(activeTab === "SUGGEST" || activeTab === "COMPARE") && (
              <>
                <div>
                  <h4 className="text-slate-400 text-xs font-semibold uppercase">Analysis</h4>
                  <p className="text-slate-200 mt-1">{result.data.reason || result.data.analysis}</p>
                </div>
                <div className="mt-4">
                  <h4 className="text-slate-400 text-xs font-semibold uppercase mb-2">Suggested Value (Editable)</h4>
                  <input 
                    type="text" 
                    value={editedValue} 
                    onChange={(e) => setEditedValue(e.target.value)} 
                    className="w-full bg-slate-800 border border-slate-600 rounded p-2 text-white"
                  />
                </div>
                
                <div className="mt-6 border-t border-slate-700 pt-4 flex space-x-3">
                  <button onClick={() => handleAction("ACCEPT")} className="flex-1 bg-green-600 hover:bg-green-700 text-white py-2 rounded flex justify-center items-center">
                    <Check className="w-4 h-4 mr-1" /> Accept As Is
                  </button>
                  <button onClick={() => handleAction("EDIT")} className="flex-1 bg-blue-600 hover:bg-blue-700 text-white py-2 rounded flex justify-center items-center">
                    <Edit className="w-4 h-4 mr-1" /> Edit & Accept
                  </button>
                  <button onClick={() => handleAction("REJECT")} className="flex-1 bg-red-600/20 hover:bg-red-600/40 text-red-400 py-2 rounded flex justify-center items-center">
                    <X className="w-4 h-4 mr-1" /> Reject
                  </button>
                </div>
              </>
            )}

            {/* Display Note */}
            {activeTab === "NOTE" && (
              <>
                <div>
                  <h4 className="text-slate-400 text-xs font-semibold uppercase">Generated Note</h4>
                  <textarea 
                    value={editedValue || result.data.note}
                    onChange={(e) => setEditedValue(e.target.value)}
                    className="w-full h-32 bg-slate-800 border border-slate-600 rounded p-3 text-white mt-2"
                  />
                </div>
                <div className="mt-4 flex space-x-3">
                  <button onClick={() => handleAction("ACCEPT")} className="flex-1 bg-blue-600 hover:bg-blue-700 text-white py-2 rounded">
                    Save to Audit
                  </button>
                </div>
              </>
            )}
            
            <div className="text-xs text-slate-500 mt-6 pt-4 border-t border-slate-800">
              Note: Accepting an AI suggestion logs it in the audit trail but does NOT automatically alter canonical data. Final decisions must be made by the human reviewer.
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
