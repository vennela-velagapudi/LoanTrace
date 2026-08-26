import Link from "next/link";

export default function Home() {
  return (
    <div className="flex-1 flex flex-col items-center justify-center p-8 text-center relative overflow-hidden">
      <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[800px] h-[800px] bg-[var(--primary)] rounded-full blur-[150px] opacity-10"></div>
      
      <div className="relative z-10 max-w-2xl">
        <h1 className="text-5xl font-bold tracking-tight mb-6 bg-clip-text text-transparent bg-gradient-to-r from-white to-[var(--muted-foreground)]">
          Loan Data Verification Copilot
        </h1>
        <p className="text-xl text-[var(--muted-foreground)] mb-10 leading-relaxed">
          An AI-powered platform for Data Operators and Reviewers to ingest, validate, and securely verify complex loan data.
        </p>
        <div className="flex justify-center gap-4">
          <Link href="/login" className="bg-white text-black px-8 py-3 rounded-full font-semibold hover:bg-gray-200 transition-colors shadow-[0_0_20px_rgba(255,255,255,0.3)]">
            Get Started
          </Link>
          <a href="https://github.com/vennela-velagapudi/LoanTrace" target="_blank" rel="noreferrer" className="bg-[var(--secondary)] text-white px-8 py-3 rounded-full font-semibold hover:bg-[var(--muted)] transition-colors border border-[var(--border)]">
            View Source
          </a>
        </div>
      </div>
    </div>
  );
}
