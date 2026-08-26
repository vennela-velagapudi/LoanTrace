export default function LoginPage() {
  return (
    <div className="min-h-[calc(100vh-4rem)] flex items-center justify-center p-4">
      <div className="glass-panel w-full max-w-md p-8 rounded-2xl relative overflow-hidden">
        {/* Decorative elements */}
        <div className="absolute -top-24 -right-24 w-48 h-48 bg-[var(--primary)] rounded-full blur-[100px] opacity-20"></div>
        <div className="absolute -bottom-24 -left-24 w-48 h-48 bg-[var(--accent)] rounded-full blur-[100px] opacity-20"></div>
        
        <div className="relative z-10">
          <div className="text-center mb-8">
            <div className="w-12 h-12 rounded-xl bg-primary flex items-center justify-center font-bold text-white shadow-[0_0_20px_rgba(59,130,246,0.6)] mx-auto mb-4 text-xl">LT</div>
            <h1 className="text-2xl font-bold tracking-tight mb-2">Welcome to LoanTrace</h1>
            <p className="text-[var(--muted-foreground)] text-sm">Sign in to access your dashboard</p>
          </div>

          <form className="space-y-4">
            <div>
              <label className="block text-sm font-medium mb-1">Username</label>
              <input 
                type="text" 
                className="w-full bg-[var(--card)] border border-[var(--border)] rounded-md px-4 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-[var(--primary)] transition-all"
                placeholder="operator, reviewer, or consumer"
              />
            </div>
            <div>
              <label className="block text-sm font-medium mb-1">Password</label>
              <input 
                type="password" 
                className="w-full bg-[var(--card)] border border-[var(--border)] rounded-md px-4 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-[var(--primary)] transition-all"
                placeholder="••••••••"
              />
            </div>
            <button 
              type="button" 
              className="w-full bg-white text-black font-semibold rounded-md py-2 mt-4 hover:bg-gray-200 transition-colors"
            >
              Sign In
            </button>
          </form>

          <div className="mt-8 pt-6 border-t border-[var(--border)] text-center">
            <p className="text-xs text-[var(--muted-foreground)] mb-2">Demo Credentials</p>
            <div className="flex justify-center gap-2 text-xs">
              <span className="px-2 py-1 bg-[var(--secondary)] rounded">operator</span>
              <span className="px-2 py-1 bg-[var(--secondary)] rounded">reviewer</span>
              <span className="px-2 py-1 bg-[var(--secondary)] rounded">consumer</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
