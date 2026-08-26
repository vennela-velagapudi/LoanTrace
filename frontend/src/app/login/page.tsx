"use client";
import { useState } from "react";
import { useRouter } from "next/navigation";
import { setToken, parseJwt } from "@/lib/auth";

export default function LoginPage() {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const router = useRouter();

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setIsLoading(true);
    
    try {
      const formData = new URLSearchParams();
      formData.append("username", username);
      formData.append("password", password);
      
      const res = await fetch("http://localhost:8000/api/auth/token", {
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
    setPassword("demo123");
  };

  return (
    <div className="min-h-[calc(100vh-4rem)] flex items-center justify-center p-4">
      <div className="glass-panel w-full max-w-md p-8 rounded-2xl relative overflow-hidden">
        {/* Decorative elements */}
        <div className="absolute -top-24 -right-24 w-48 h-48 bg-[var(--primary)] rounded-full blur-[100px] opacity-20"></div>
        <div className="absolute -bottom-24 -left-24 w-48 h-48 bg-[var(--accent)] rounded-full blur-[100px] opacity-20"></div>
        
        <div className="relative z-10">
          <div className="text-center mb-8">
            <div className="w-12 h-12 rounded-xl bg-primary flex items-center justify-center font-bold text-white shadow-[0_0_20px_rgba(59,130,246,0.6)] mx-auto mb-4 text-xl">LT</div>
            <h1 className="text-2xl font-bold tracking-tight mb-2">LoanTrace Verification</h1>
            <p className="text-[var(--muted-foreground)] text-sm">Sign in with your role credentials</p>
          </div>

          <form className="space-y-4" onSubmit={handleLogin}>
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
              <input 
                type="password" 
                className="w-full bg-[var(--background)] border border-[var(--border)] rounded-md px-4 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-[var(--primary)] transition-all"
                placeholder="••••••••"
                value={password}
                onChange={e => setPassword(e.target.value)}
                required
              />
            </div>
            <button 
              type="submit" 
              disabled={isLoading}
              className="w-full bg-[var(--primary)] text-white font-semibold rounded-md py-2 mt-4 hover:opacity-90 transition-opacity disabled:opacity-50"
            >
              {isLoading ? "Signing in..." : "Sign In"}
            </button>
          </form>

          <div className="mt-8 pt-6 border-t border-[var(--border)] text-center">
            <p className="text-xs text-[var(--muted-foreground)] mb-2">Demo Credentials (click to autofill)</p>
            <div className="flex justify-center gap-2 text-xs">
              <button type="button" onClick={() => autofill("operator")} className="px-2 py-1 bg-[var(--secondary)] hover:bg-[var(--border)] rounded transition-colors">operator</button>
              <button type="button" onClick={() => autofill("reviewer")} className="px-2 py-1 bg-[var(--secondary)] hover:bg-[var(--border)] rounded transition-colors">reviewer</button>
              <button type="button" onClick={() => autofill("consumer")} className="px-2 py-1 bg-[var(--secondary)] hover:bg-[var(--border)] rounded transition-colors">consumer</button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
