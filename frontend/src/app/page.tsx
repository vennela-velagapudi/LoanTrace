import Link from "next/link";

export default function Home() {
  return (
    <div className="flex-1 flex flex-col items-center justify-center p-4 sm:p-8 text-center relative overflow-hidden bg-slate-50">
      <div className="relative z-10 max-w-2xl">
        <h1 className="text-4xl md:text-5xl font-bold tracking-tight mb-6 text-slate-900">
          Loan Data Verification Copilot
        </h1>
        <p className="text-xl text-slate-600 mb-10 leading-relaxed">
          An AI-powered platform for Data Operators and Reviewers to ingest, validate, and securely verify complex loan data.
        </p>
        <div className="flex justify-center gap-4">
          <Link href="/login" className="bg-blue-600 text-white px-8 py-3 rounded-md font-semibold hover:bg-blue-700 transition-colors shadow-sm">
            Get Started
          </Link>
        </div>
      </div>
    </div>
  );
}
