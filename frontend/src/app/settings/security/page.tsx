"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { apiFetch, getToken, getUserRole, getUsername, markPasswordChanged } from "@/lib/auth";
import { Eye, EyeOff } from "lucide-react";
import Link from "next/link";

export default function SecuritySettings() {
  const router = useRouter();
  
  const [currentPassword, setCurrentPassword] = useState("");
  const [newPassword, setNewPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [pwdMsg, setPwdMsg] = useState("");
  const [pwdError, setPwdError] = useState("");
  const [isChangingPwd, setIsChangingPwd] = useState(false);
  const [role, setRole] = useState<string | null>(null);
  const [showCurrent, setShowCurrent] = useState(false);
  const [showNew, setShowNew] = useState(false);
  const [showConfirm, setShowConfirm] = useState(false);

  useEffect(() => {
    const t = getToken();
    if (!t) {
      router.push("/login");
      return;
    }
    setRole(getUserRole());
  }, [router]);

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
      
      setPwdMsg("Password changed successfully. Please use your updated password the next time you sign in.");
      
      const user = getUsername();
      if (user) {
        markPasswordChanged(user);
      }
      

      setCurrentPassword("");
      setNewPassword("");
      setConfirmPassword("");
    } catch (err: any) {
      setPwdError(err.message);
    } finally {
      setIsChangingPwd(false);
    }
  };

  const dashboardRoute = 
    role === "DATA_OPERATOR" ? "/operator" :
    role === "REVIEWER" ? "/reviewer" :
    role === "DATA_CONSUMER" ? "/consumer" : "/";

  return (
    <div className="p-4 sm:p-8 max-w-2xl mx-auto">
      <Link href={dashboardRoute} className="text-sm text-slate-500 hover:text-slate-800 mb-6 inline-block">← Back to Dashboard</Link>
      
      <div className="glass-panel p-6 sm:p-8 rounded-xl bg-white shadow-sm border border-slate-200">
        <h1 className="text-2xl font-bold tracking-tight mb-2 text-slate-900">Security Settings</h1>
        <p className="text-sm text-slate-500 mb-8 border-b border-slate-200 pb-6">Update your password securely.</p>
        
        <form onSubmit={handleChangePassword} className="space-y-5 max-w-md">
          {pwdError && <div className="p-3 bg-red-50 border border-red-200 text-red-700 rounded-md text-sm">{pwdError}</div>}
          {pwdMsg && <div className="p-3 bg-green-50 border border-green-200 text-green-700 rounded-md text-sm">{pwdMsg}</div>}
          
          <div>
            <label className="block text-sm font-medium mb-1 text-slate-700">Current Password</label>
            <div className="relative">
              <input 
                type={showCurrent ? "text" : "password"} 
                className="w-full bg-slate-50 border border-slate-300 rounded-md px-4 py-2 pr-10 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 transition-all text-slate-900"
                value={currentPassword}
                onChange={e => setCurrentPassword(e.target.value)}
                required
              />
              <button
                type="button"
                onClick={() => setShowCurrent(!showCurrent)}
                className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600 cursor-pointer"
                title={showCurrent ? "Hide password" : "Show password"}
              >
                {showCurrent ? <EyeOff size={16} /> : <Eye size={16} />}
              </button>
            </div>
          </div>
          <div>
            <label className="block text-sm font-medium mb-1 text-slate-700">New Password</label>
            <div className="relative">
              <input 
                type={showNew ? "text" : "password"} 
                className="w-full bg-slate-50 border border-slate-300 rounded-md px-4 py-2 pr-10 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 transition-all text-slate-900"
                value={newPassword}
                onChange={e => setNewPassword(e.target.value)}
                required
              />
              <button
                type="button"
                onClick={() => setShowNew(!showNew)}
                className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600 cursor-pointer"
                title={showNew ? "Hide password" : "Show password"}
              >
                {showNew ? <EyeOff size={16} /> : <Eye size={16} />}
              </button>
            </div>
          </div>
          <div>
            <label className="block text-sm font-medium mb-1 text-slate-700">Confirm New Password</label>
            <div className="relative">
              <input 
                type={showConfirm ? "text" : "password"} 
                className="w-full bg-slate-50 border border-slate-300 rounded-md px-4 py-2 pr-10 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 transition-all text-slate-900"
                value={confirmPassword}
                onChange={e => setConfirmPassword(e.target.value)}
                required
              />
              <button
                type="button"
                onClick={() => setShowConfirm(!showConfirm)}
                className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600 cursor-pointer"
                title={showConfirm ? "Hide password" : "Show password"}
              >
                {showConfirm ? <EyeOff size={16} /> : <Eye size={16} />}
              </button>
            </div>
          </div>
          
          <div className="pt-2">
            <button 
              type="submit" 
              disabled={isChangingPwd || !currentPassword || !newPassword || !confirmPassword}
              className={`w-full py-2.5 rounded-md font-medium transition-colors text-sm shadow-sm cursor-pointer ${
                isChangingPwd || !currentPassword || !newPassword || !confirmPassword ? 'bg-slate-200 text-slate-500 cursor-not-allowed' : 'bg-slate-800 hover:bg-slate-900 text-white'
              }`}
            >
              {isChangingPwd ? "Updating..." : "Change Password"}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
