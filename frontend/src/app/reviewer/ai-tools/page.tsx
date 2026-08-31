"use client";
import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { Bot, Sparkles, Activity, FileCode } from "lucide-react";
import { apiFetch, getToken, getUserRole } from "@/lib/auth";

export default function AITools() {
  const router = useRouter();
  const [loading, setLoading] = useState(false);
  const [activeTab, setActiveTab] = useState("SUMMARY");

  // Summary state
  const [exceptions, setExceptions] = useState<any[]>([]);
  const [selectedExceptions, setSelectedExceptions] = useState<number[]>([]);
  const [summaryResult, setSummaryResult] = useState<any>(null);

  // Rule gen state
  const [naturalLanguage, setNaturalLanguage] = useState("");
  const [ruleResult, setRuleResult] = useState<any>(null);

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
    
    // Fetch OPEN exceptions for summary
    const fetchExceptions = async () => {
      try {
        const res = await apiFetch("/api/exceptions");
        if (res.ok) {
          const data = await res.json();
          setExceptions(data.filter((e: any) => e.status === "OPEN"));
        }
      } catch (e) {
        console.error(e);
      }
    };
    fetchExceptions();
  }, [router]);

  const handleGenerateSummary = async () => {
    if (selectedExceptions.length === 0) {
      alert("Please select at least one exception to summarize.");
      return;
    }
    setLoading(true);
    setSummaryResult(null);
    try {
      const res = await apiFetch("/api/ai/batch-summary", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ exception_ids: selectedExceptions })
      });
      if (res.ok) {
        const data = await res.json();
        setSummaryResult(data.data);
      } else {
        alert(`Batch Summary API Error: ${res.status} - ${await res.text()}`);
      }
    } catch (e) {
      console.error(e);
      alert(`Network/Client Error: ${e}`);
    } finally {
      setLoading(false);
    }
  };

  const handleGenerateRule = async () => {
    if (!naturalLanguage.trim()) return;
    setLoading(true);
    setRuleResult(null);
    try {
      const res = await apiFetch("/api/ai/generate-rule", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ natural_language: naturalLanguage })
      });
      if (res.ok) {
        const data = await res.json();
        setRuleResult(data.data);
      } else {
        alert(`Rule Generator API Error: ${res.status} - ${await res.text()}`);
      }
    } catch (e) {
      console.error(e);
      alert(`Network/Client Error: ${e}`);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="p-4 sm:p-8 max-w-5xl mx-auto text-slate-900">
      <Link href="/reviewer" className="text-sm text-slate-500 hover:text-slate-900 mb-6 inline-block">← Back to Dashboard</Link>
      
      <div className="flex items-center gap-4 mb-8">
        <Bot className="w-10 h-10 text-purple-400" />
        <div>
          <h1 className="text-3xl font-bold">AI Tools Workspace</h1>
          <p className="text-slate-500">Generate batch insights and natural language validation rules.</p>
        </div>
      </div>

      <div className="flex gap-4 mb-6 border-b border-slate-200 pb-2">
        <button 
          onClick={() => setActiveTab("SUMMARY")}
          className={`flex items-center gap-2 px-4 py-2 rounded-t-lg font-semibold ${activeTab === 'SUMMARY' ? 'text-purple-700 border-b-2 border-purple-700' : 'text-slate-500 hover:text-slate-900'}`}
        >
          <Activity className="w-5 h-5" /> Batch Summary
        </button>
        <button 
          onClick={() => setActiveTab("RULE")}
          className={`flex items-center gap-2 px-4 py-2 rounded-t-lg font-semibold ${activeTab === 'RULE' ? 'text-purple-700 border-b-2 border-purple-700' : 'text-slate-500 hover:text-slate-900'}`}
        >
          <Sparkles className="w-5 h-5" /> Rule Generator
        </button>
      </div>

      {activeTab === "SUMMARY" && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
          <div className="bg-white border border-slate-200 shadow-sm p-6 rounded-lg">
            <h3 className="text-lg font-semibold mb-4 text-slate-900">Select Exceptions</h3>
            <div className="space-y-2 max-h-96 overflow-y-auto pr-2">
              {exceptions.map(exc => (
                <label key={exc.id} className="flex items-start gap-3 p-3 bg-slate-50 rounded border border-slate-200 cursor-pointer hover:border-purple-500">
                  <input 
                    type="checkbox" 
                    className="mt-1"
                    checked={selectedExceptions.includes(exc.id)}
                    onChange={(e) => {
                      if (e.target.checked) setSelectedExceptions([...selectedExceptions, exc.id]);
                      else setSelectedExceptions(selectedExceptions.filter(id => id !== exc.id));
                    }}
                  />
                  <div>
                    <div className="font-semibold text-sm">EXC-{exc.id} • <span className="text-red-600 font-bold">{exc.severity}</span></div>
                    <div className="text-xs text-slate-500 mt-1">{exc.rule_name}</div>
                  </div>
                </label>
              ))}
              {exceptions.length === 0 && <div className="text-slate-500">No open exceptions available.</div>}
            </div>
            
            <button 
              className="mt-6 w-full py-2 bg-purple-600 hover:bg-purple-700 rounded font-semibold disabled:opacity-50"
              onClick={handleGenerateSummary}
              disabled={loading || selectedExceptions.length === 0}
            >
              {loading ? "Generating..." : "Generate AI Summary"}
            </button>
          </div>

          <div className="bg-white border border-slate-200 shadow-sm p-6 rounded-lg">
            <h3 className="text-lg font-semibold mb-4 text-slate-900">AI Summary Output</h3>
            {!summaryResult && !loading && <div className="text-slate-500 text-center mt-10">Select exceptions and generate a summary.</div>}
            {loading && <div className="text-purple-700 text-center mt-10 animate-pulse flex flex-col items-center"><Bot className="w-8 h-8 mb-2" /> Analyzing batch...</div>}
            
            {summaryResult && (
              <div className="space-y-6 text-sm text-slate-700">
                <div className="grid grid-cols-2 gap-4">
                  <div className="bg-slate-50 p-4 rounded border border-slate-200">
                    <div className="text-slate-500 uppercase text-xs font-bold mb-1">Exceptions Analyzed</div>
                    <div className="text-2xl font-mono">{summaryResult.total_exceptions_analyzed}</div>
                  </div>
                  <div className="bg-slate-50 p-4 rounded border border-slate-200">
                    <div className="text-slate-500 uppercase text-xs font-bold mb-1">Most Common Rule</div>
                    <div className="font-mono text-purple-700">{summaryResult.most_common_rules[0] || 'N/A'}</div>
                  </div>
                </div>
                
                <div>
                  <h4 className="text-slate-500 uppercase text-xs font-bold mb-2">Severity Distribution</h4>
                  <div className="flex flex-wrap gap-2">
                    {summaryResult.severity_distribution.map((item: any) => (
                      <div key={item.severity} className="bg-slate-50 px-3 py-1 rounded text-xs border border-slate-200">
                        <span className={item.severity === 'CRITICAL' ? 'text-red-500 font-bold' : item.severity === 'HIGH' ? 'text-orange-500 font-bold' : 'text-yellow-500 font-bold'}>{item.severity}</span>: {item.count}
                      </div>
                    ))}
                  </div>
                </div>

                <div>
                  <h4 className="text-slate-500 uppercase text-xs font-bold mb-2">Identified Patterns</h4>
                  <p className="bg-slate-50 p-3 rounded border border-slate-200">{summaryResult.patterns}</p>
                </div>

                <div>
                  <h4 className="text-slate-500 uppercase text-xs font-bold mb-2">AI Recommended Priorities</h4>
                  <p className="bg-slate-50 p-3 rounded border border-slate-200">{summaryResult.recommendations}</p>
                </div>
                
                <div className="text-xs text-slate-500 text-center">AI Batch Summary is for informational purposes only.</div>
              </div>
            )}
          </div>
        </div>
      )}

      {activeTab === "RULE" && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
          <div className="bg-white border border-slate-200 shadow-sm p-6 rounded-lg flex flex-col">
            <h3 className="text-lg font-semibold mb-4 text-slate-900">Natural Language Request</h3>
            <p className="text-slate-500 text-sm mb-4">Describe the validation rule you want to create in plain English.</p>
            
            <textarea 
              className="w-full bg-slate-50 bg-white border border-slate-300 focus:border-purple-500 focus:ring-1 focus:ring-purple-500 rounded p-4 text-slate-900 flex-1 min-h-[200px]"
              placeholder='e.g., "Flag any loan where the current balance is greater than 90% of the original principal."'
              value={naturalLanguage}
              onChange={(e) => setNaturalLanguage(e.target.value)}
            />
            
            <button 
              className="mt-6 w-full py-2 bg-purple-600 hover:bg-purple-700 rounded font-semibold flex items-center justify-center gap-2 disabled:opacity-50"
              onClick={handleGenerateRule}
              disabled={loading || !naturalLanguage}
            >
              <Sparkles className="w-4 h-4" /> {loading ? "Generating..." : "Generate Rule"}
            </button>
          </div>

          <div className="bg-white border border-slate-200 shadow-sm p-6 rounded-lg">
            <h3 className="text-lg font-semibold mb-4 text-slate-900 flex items-center justify-between">
              <span>Proposed Rule</span>
              {ruleResult && <span className="bg-orange-500/20 text-orange-400 text-xs px-2 py-1 rounded font-normal uppercase tracking-wider">Requires Human Approval</span>}
            </h3>
            
            {!ruleResult && !loading && <div className="text-slate-500 text-center mt-10">Enter a description and generate a rule.</div>}
            {loading && <div className="text-purple-700 text-center mt-10 animate-pulse flex flex-col items-center"><Bot className="w-8 h-8 mb-2" /> Designing rule...</div>}
            
            {ruleResult && (
              <div className="space-y-4 text-sm text-slate-700">
                <div>
                  <span className="text-slate-500 uppercase text-xs font-bold block mb-1">Rule Name</span>
                  <div className="font-mono text-slate-800 bg-slate-50 px-3 py-2 rounded border border-slate-200">{ruleResult.rule_name}</div>
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <span className="text-slate-500 uppercase text-xs font-bold block mb-1">Target Field</span>
                    <div className="font-mono text-blue-700 bg-slate-50 border border-slate-200 px-3 py-2 rounded">{ruleResult.target_field}</div>
                  </div>
                  <div>
                    <span className="text-slate-500 uppercase text-xs font-bold block mb-1">Suggested Severity</span>
                    <div className="font-mono text-red-700 bg-slate-50 border border-slate-200 px-3 py-2 rounded">{ruleResult.suggested_severity}</div>
                  </div>
                </div>
                <div>
                  <span className="text-slate-500 uppercase text-xs font-bold block mb-1">Logic Pattern</span>
                  <div className="bg-slate-50 p-3 rounded font-mono text-xs flex gap-2">
                    <span className="text-purple-700">{ruleResult.target_field}</span>
                    <span className="text-green-700">{ruleResult.operator}</span>
                    <span className="text-yellow-600 font-bold">{ruleResult.threshold}</span>
                  </div>
                </div>
                <div>
                  <span className="text-slate-500 uppercase text-xs font-bold block mb-1">Validation Pseudocode</span>
                  <pre className="bg-slate-100 p-3 rounded font-mono text-xs overflow-x-auto border border-slate-300 text-slate-700">
                    {ruleResult.validation_pseudocode}
                  </pre>
                </div>
                <div>
                  <span className="text-slate-500 uppercase text-xs font-bold block mb-1">Test Cases</span>
                  <ul className="list-disc pl-5 space-y-1 bg-slate-50 p-3 rounded">
                    {ruleResult.test_cases.map((tc: string, i: number) => <li key={i} className="font-mono text-xs">{tc}</li>)}
                  </ul>
                </div>
                
                <div className="pt-4 mt-4 border-t border-slate-200 flex gap-3">
                  <button className="flex-1 bg-green-600 hover:bg-green-700 text-white py-2 rounded font-semibold" onClick={() => alert("Rule accepted (Mock: Not actually deployed to engine)")}>Accept Proposal</button>
                  <button className="flex-1 bg-slate-700 hover:bg-slate-600 text-white py-2 rounded font-semibold" onClick={() => setRuleResult(null)}>Reject</button>
                </div>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
