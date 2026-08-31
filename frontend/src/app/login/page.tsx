"use client";
import { useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { setToken, parseJwt, hasPasswordChanged } from "@/lib/auth";
import { Eye, EyeOff } from "lucide-react";

export default function LoginPage() {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [infoMessage, setInfoMessage] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [showPassword, setShowPassword] = useState(false);
  const router = useRouter();

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setInfoMessage("");
    setIsLoading(true);
    
    try {
      const formData = new URLSearchParams();
      formData.append("username", username);
      formData.append("password", password);
      
      let API_URL = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";
      if (API_URL.includes("localhost:8000") || API_URL.includes(":8001") || API_URL.includes(":8002") || API_URL.includes(":8004")) {
        API_URL = "http://127.0.0.1:8000";
      }
      const res = await fetch(`${API_URL}/api/auth/token`, {
        method: "POST",
        headers: { "Content-Type": "application/x-www-form-urlencoded" },
        body: formData.toString()
      });
      
      if (!res.ok) {
        throw new Error("Invalid username or password");
      }
      
      const data = await res.json();
      setToken(data.access_token);
      
      const decoded = parseJwt(data.access_token);
      
      // Redirect based on role
      if (decoded?.role === "DATA_OPERATOR") {
        router.push("/operator");
      } else if (decoded?.role === "REVIEWER") {
        router.push("/reviewer");
      } else if (decoded?.role === "DATA_CONSUMER") {
        router.push("/consumer");
      } else {
        router.push("/");
      }
    } catch (err: any) {
      setError(err.message);
    } finally {
      setIsLoading(false);
    }
  };

  const autofill = (u: string) => {
    setUsername(u);
    setPassword("");
    setError("");
    if (hasPasswordChanged(u)) {
      setInfoMessage("Your password was changed. Please enter your updated password.");
    } else {
      setInfoMessage("");
    }
  };

  return (
    <div className="min-h-[calc(100vh-4rem)] flex items-center justify-center p-4">
      <div className="glass-panel w-full max-w-md p-6 sm:p-8 rounded-2xl relative overflow-hidden">
        
        <div className="relative z-10">
          <div className="text-center mb-8">
            <Link 
              href="/" 
              className="w-12 h-12 rounded-xl bg-primary flex items-center justify-center font-bold text-white mx-auto mb-4 text-xl cursor-pointer hover:opacity-90 transition-opacity"
            >
              LT
            </Link>
            <h1 className="text-2xl font-bold tracking-tight mb-2">LoanTrace Verification</h1>
            <p className="text-[var(--muted-foreground)] text-sm">Sign in with your role credentials</p>
          </div>

          <form className="space-y-4" onSubmit={handleLogin}>
            {infoMessage && (
              <div className="p-3 bg-blue-50 border border-blue-200 rounded text-blue-700 text-sm text-center">
                {infoMessage}
              </div>
            )}
            {error && (
              <div className="p-3 bg-red-500/20 border border-red-500/50 rounded text-red-400 text-sm text-center">
                {error}
              </div>
            )}
            <div>
              <label className="block text-sm font-medium mb-1">Username</label>
              <input 
                type="text" 
                className="w-full bg-[var(--background)] border border-[var(--border)] rounded-md px-4 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-[var(--primary)] transition-all"
                placeholder="operator, reviewer, or consumer"
                value={username}
                onChange={e => setUsername(e.target.value)}
                required
              />
            </div>
            <div>
              <label className="block text-sm font-medium mb-1">Password</label>
              <div className="relative">
                <input 
                  type={showPassword ? "text" : "password"} 
                  className="w-full bg-[var(--background)] border border-[var(--border)] rounded-md px-4 py-2 pr-10 text-sm focus:outline-none focus:ring-2 focus:ring-[var(--primary)] transition-all"
                  placeholder="••••••••"
                  value={password}
                  onChange={e => setPassword(e.target.value)}
                  required
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-200 cursor-pointer"
                  title={showPassword ? "Hide password" : "Show password"}
                >
                  {showPassword ? <EyeOff size={16} /> : <Eye size={16} />}
                </button>
              </div>
            </div>
            <button 
              type="submit" 
              disabled={isLoading}
              className="w-full bg-[var(--primary)] text-white font-semibold rounded-md py-2 mt-4 hover:opacity-90 hover:bg-blue-600 transition-colors disabled:opacity-50 cursor-pointer"
            >
              {isLoading ? "Signing in..." : "Sign In"}
            </button>
          </form>

          <div className="mt-8 pt-6 border-t border-[var(--border)] text-center">
            <p className="text-xs text-[var(--muted-foreground)] mb-1 font-medium">Demo Credentials (click to autofill)</p>
            <p className="text-[11px] text-slate-400 mb-4">(Initial demo password: <code className="bg-slate-100 px-1 py-0.5 rounded text-slate-600 font-mono">demo123</code> &mdash; until you change it manually from the dashboard.)</p>
            <div className="flex flex-wrap justify-center gap-2 text-xs">
              <button type="button" onClick={() => autofill("operator")} className="px-3 py-1.5 bg-[var(--secondary)] hover:bg-[var(--border)] hover:scale-105 rounded cursor-pointer transition-all">operator</button>
              <button type="button" onClick={() => autofill("reviewer")} className="px-3 py-1.5 bg-[var(--secondary)] hover:bg-[var(--border)] hover:scale-105 rounded cursor-pointer transition-all">reviewer</button>
              <button type="button" onClick={() => autofill("consumer")} className="px-3 py-1.5 bg-[var(--secondary)] hover:bg-[var(--border)] hover:scale-105 rounded cursor-pointer transition-all">consumer</button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
