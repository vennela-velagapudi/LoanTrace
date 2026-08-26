import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "LoanTrace | AI FinTech Copilot",
  description: "Loan Data Verification Copilot",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className="dark">
      <body
        className={`${geistSans.variable} ${geistMono.variable} antialiased min-h-screen flex flex-col`}
      >
        <header className="border-b border-[var(--border)] glass-panel sticky top-0 z-50">
          <div className="container mx-auto px-4 h-16 flex items-center justify-between">
            <div className="flex items-center gap-2">
              <div className="w-8 h-8 rounded bg-primary flex items-center justify-center font-bold text-white shadow-[0_0_15px_rgba(59,130,246,0.5)]">LT</div>
              <span className="font-semibold text-xl tracking-tight">LoanTrace</span>
            </div>
            <nav className="flex items-center gap-6 text-sm text-[var(--muted-foreground)]">
              <a href="/operator" className="hover:text-white transition-colors">Operator</a>
              <a href="/reviewer" className="hover:text-white transition-colors">Reviewer</a>
              <a href="/consumer" className="hover:text-white transition-colors">Consumer</a>
              <a href="/login" className="px-4 py-2 rounded-md bg-secondary text-white hover:bg-[var(--accent)] transition-colors">Login</a>
            </nav>
          </div>
        </header>
        <main className="flex-1 flex flex-col">
          {children}
        </main>
      </body>
    </html>
  );
}
