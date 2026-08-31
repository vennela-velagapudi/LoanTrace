"use client";

import { useState, useEffect, useRef } from "react";
import { useRouter } from "next/navigation";
import { apiFetch, getToken, getUserRole } from "@/lib/auth";

type UploadSummary = {
  filename: string;
  total_rows: number;
  normalized_count: number;
  failed_count: number;
  exceptions_created: number;
  status?: string;
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
  const fileInputRef = useRef<HTMLInputElement>(null);
  
  // Password Change State
  const [currentPassword, setCurrentPassword] = useState("");
  const [newPassword, setNewPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [pwdMsg, setPwdMsg] = useState("");
  const [pwdError, setPwdError] = useState("");
  const [isChangingPwd, setIsChangingPwd] = useState(false);

  const handleChangePassword = async (e: React.FormEvent) => {
    e.preventDefault();
    setPwdError("");
    setPwdMsg("");
    
    if (newPassword !== confirmPassword) {
      setPwdError("New passwords do not match");
      return;
    }
    
    setIsChangingPwd(true);
    try {
      const res = await apiFetch("/api/auth/change-password", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ current_password: currentPassword, new_password: newPassword }),
      });
      
      const data = await res.json();
      if (!res.ok) {
        throw new Error(data.detail || "Failed to change password");
      }
      
      setPwdMsg("Password changed successfully.");
      setCurrentPassword("");
      setNewPassword("");
      setConfirmPassword("");
    } catch (err: any) {
      setPwdError(err.message);
    } finally {
      setIsChangingPwd(false);
    }
  };
  const [uploading, setUploading] = useState(false);
  const [summary, setSummary] = useState<UploadSummary | null>(null);
  const [error, setError] = useState("");

  useEffect(() => {
    const fetchLatestSummary = async () => {
      try {
        const res = await apiFetch("/api/files/latest/summary");
        if (res.ok) {
          const data = await res.json();
          if (data && data.filename) {
            setSummary(data);
          }
        }
      } catch (err) {
        console.error("Failed to fetch latest summary", err);
      }
    };
    fetchLatestSummary();
  }, []);

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
    <div className="p-4 sm:p-8">
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 sm:gap-0 mb-6 sm:mb-8">
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
            ref={fileInputRef}
            className="hidden"
            id="fileInput"
          />
          <div className="flex flex-col items-center gap-2 mb-6 relative z-10 w-full max-w-xs">
            <button 
              type="button"
              onClick={() => fileInputRef.current?.click()}
              className="w-full px-4 py-2 bg-slate-100 hover:bg-slate-200 border border-slate-300 text-slate-800 rounded-md cursor-pointer font-medium shadow-sm transition-colors text-sm"
            >
              Choose File
            </button>
            <span className="text-xs text-slate-500 max-w-full truncate px-2 text-center pointer-events-none">
              {file ? file.name : "No file chosen"}
            </span>
          </div>

          <button 
            onClick={handleUpload}
            disabled={!file || uploading}
            className={`px-6 py-2 rounded-md font-medium transition-colors relative z-10 w-full max-w-xs ${
              !file || uploading ? 'bg-slate-200 text-slate-500 cursor-not-allowed' : 'bg-[var(--primary)] hover:bg-blue-700 text-white shadow-sm cursor-pointer'
            }`}
          >
            {uploading ? "Uploading & Processing..." : "Start Ingestion"}
          </button>

          {error && (
            <div className="mt-4 p-3 bg-red-50 border border-red-200 text-red-700 rounded-md text-sm w-full max-w-xs relative z-10">
              {error}
            </div>
          )}
        </div>

        {/* Summary Panel */}
        <div className="glass-panel p-8 rounded-xl flex flex-col">
          <h2 className="text-xl font-semibold mb-6 border-b border-[var(--border)] pb-4">Ingestion Summary</h2>
          
          {!summary && !uploading && (
            <div className="flex-1 flex flex-col items-center justify-center text-[var(--muted-foreground)]">
              <div className="text-4xl mb-4 opacity-50">📊</div>
              <p>Upload a file to see the ingestion and validation results.</p>
            </div>
          )}

          {uploading && (
            <div className="flex-1 flex flex-col items-center justify-center text-[var(--primary)]">
              <div className="w-8 h-8 border-4 border-[var(--primary)] border-t-transparent rounded-full animate-spin mb-4"></div>
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
                <span className="font-semibold text-[var(--success)]">{summary.status}</span>
              </div>
              <div className="flex justify-between items-center p-3 bg-[var(--secondary)] rounded-lg">
                <span className="text-[var(--muted-foreground)]">Total Rows</span>
                <span className="font-bold">{summary.total_rows}</span>
              </div>
              <div className="flex justify-between items-center p-3 bg-[var(--secondary)] rounded-lg">
                <span className="text-[var(--muted-foreground)]">Successful Normalizations</span>
                <span className="font-bold text-[var(--success)]">{summary.normalized_count}</span>
              </div>
              <div className="flex justify-between items-center p-3 bg-red-50 border border-red-200 rounded-lg">
                <span className="text-slate-600">Failed Rows (Malformed)</span>
                <span className="font-bold text-red-600">{summary.failed_count}</span>
              </div>
              <div className="flex justify-between items-center p-3 bg-indigo-50 border border-indigo-200 rounded-lg">
                <span className="text-slate-600">Validation Exceptions Generated</span>
                <span className="font-bold text-indigo-600">{summary.exceptions_created}</span>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
