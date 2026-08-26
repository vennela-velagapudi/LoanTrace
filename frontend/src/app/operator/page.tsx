"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { apiFetch, getToken, getUserRole } from "@/lib/auth";

type UploadSummary = {
  filename: string;
  total_rows: number;
  successful_rows: number;
  failed_rows: number;
  exceptions_created: number;
  status: string;
};

export default function OperatorDashboard() {
  const router = useRouter();
  const [file, setFile] = useState<File | null>(null);

  useEffect(() => {
    const t = getToken();
    if (!t) {
      router.push("/login");
      return;
    }
    const role = getUserRole();
    if (role !== "DATA_OPERATOR") {
      router.push("/login");
    }
  }, [router]);
  const [uploading, setUploading] = useState(false);
  const [summary, setSummary] = useState<UploadSummary | null>(null);
  const [error, setError] = useState("");

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      setFile(e.target.files[0]);
    }
  };

  const handleUpload = async () => {
    if (!file) return;
    setUploading(true);
    setError("");
    setSummary(null);

    const formData = new FormData();
    formData.append("file", file);

    try {
      const response = await apiFetch("/api/files/upload", {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        throw new Error("Upload failed. Server responded with " + response.status);
      }

      const data = await response.json();
      setSummary(data);
    } catch (err: any) {
      setError(err.message || "An error occurred during upload.");
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="p-8">
      <div className="flex justify-between items-center mb-8">
        <h1 className="text-3xl font-bold tracking-tight">Data Operator Dashboard</h1>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
        {/* Upload Panel */}
        <div className="glass-panel p-8 rounded-xl flex flex-col items-center justify-center border border-dashed border-[var(--border)] relative overflow-hidden">
          <div className="absolute inset-0 bg-gradient-to-br from-[var(--primary)]/10 to-transparent pointer-events-none"></div>
          
          <h2 className="text-xl font-semibold mb-4 relative z-10">Upload Loan Tape</h2>
          <p className="text-sm text-[var(--muted-foreground)] mb-6 text-center relative z-10">
            Select a CSV file containing loan records. The system will parse, normalize, and validate the data against configured rules.
          </p>

          <input 
            type="file" 
            accept=".csv"
            onChange={handleFileChange}
            className="mb-4 text-sm text-[var(--muted-foreground)]
              file:mr-4 file:py-2 file:px-4
              file:rounded-full file:border-0
              file:text-sm file:font-semibold
              file:bg-[var(--secondary)] file:text-white
              hover:file:bg-[var(--muted)] relative z-10"
          />

          <button 
            onClick={handleUpload}
            disabled={!file || uploading}
            className={`px-6 py-2 rounded-md font-medium transition-colors relative z-10 w-full max-w-xs ${
              !file || uploading ? 'bg-gray-700 text-gray-400 cursor-not-allowed' : 'bg-primary hover:bg-blue-600 text-white shadow-[0_0_15px_rgba(59,130,246,0.4)]'
            }`}
          >
            {uploading ? "Uploading & Processing..." : "Start Ingestion"}
          </button>

          {error && (
            <div className="mt-4 p-3 bg-red-950/50 border border-red-900 text-red-200 rounded-md text-sm w-full max-w-xs relative z-10">
              {error}
            </div>
          )}
        </div>

        {/* Summary Panel */}
        <div className="glass-panel p-8 rounded-xl flex flex-col">
          <h2 className="text-xl font-semibold mb-6 border-b border-[var(--border)] pb-4">Ingestion Summary</h2>
          
          {!summary && !uploading && (
            <div className="flex-1 flex flex-col items-center justify-center text-[var(--muted-foreground)]">
              <span className="text-4xl mb-4 opacity-20">📊</span>
              <p>Upload a file to see the ingestion and validation results.</p>
            </div>
          )}

          {uploading && (
            <div className="flex-1 flex flex-col items-center justify-center text-[var(--primary)]">
              <div className="w-8 h-8 border-4 border-[var(--primary)] border-t-transparent rounded-full animate-spin mb-4 shadow-[0_0_10px_rgba(59,130,246,0.5)]"></div>
              <p className="animate-pulse">Processing records...</p>
            </div>
          )}

          {summary && !uploading && (
            <div className="space-y-4 animate-in fade-in duration-500">
              <div className="flex justify-between items-center p-3 bg-[var(--secondary)] rounded-lg">
                <span className="text-[var(--muted-foreground)]">Filename</span>
                <span className="font-mono text-sm">{summary.filename}</span>
              </div>
              <div className="flex justify-between items-center p-3 bg-[var(--secondary)] rounded-lg">
                <span className="text-[var(--muted-foreground)]">Status</span>
                <span className="font-semibold text-green-400">{summary.status}</span>
              </div>
              <div className="flex justify-between items-center p-3 bg-[var(--secondary)] rounded-lg">
                <span className="text-[var(--muted-foreground)]">Total Rows</span>
                <span className="font-bold">{summary.total_rows}</span>
              </div>
              <div className="flex justify-between items-center p-3 bg-[var(--secondary)] rounded-lg">
                <span className="text-[var(--muted-foreground)]">Successful Normalizations</span>
                <span className="font-bold text-green-400">{summary.successful_rows}</span>
              </div>
              <div className="flex justify-between items-center p-3 bg-red-950/30 border border-red-900/30 rounded-lg">
                <span className="text-[var(--muted-foreground)]">Failed Rows (Malformed)</span>
                <span className="font-bold text-red-400">{summary.failed_rows}</span>
              </div>
              <div className="flex justify-between items-center p-3 bg-purple-950/30 border border-purple-900/30 rounded-lg">
                <span className="text-[var(--muted-foreground)]">Validation Exceptions Generated</span>
                <span className="font-bold text-[var(--accent)]">{summary.exceptions_created}</span>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
