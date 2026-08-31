import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import Link from "next/link";
import "./globals.css";
import ClientNav from "@/components/ClientNav";

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
    <html lang="en">
      <body
        className={`${geistSans.variable} ${geistMono.variable} antialiased min-h-screen flex flex-col`}
      >
        <header className="border-b border-[var(--border)] glass-panel sticky top-0 z-50">
          <div className="container mx-auto px-4 h-16 flex items-center justify-between">
            <Link href="/" className="flex items-center gap-2 cursor-pointer hover:opacity-90 transition-opacity">
              <div className="w-8 h-8 rounded bg-primary flex items-center justify-center font-bold text-white">LT</div>
              <span className="font-semibold text-xl tracking-tight text-[var(--foreground)]">LoanTrace</span>
            </Link>
            <ClientNav />
          </div>
        </header>
        <main className="flex-1 flex flex-col">
          {children}
        </main>
      </body>
    </html>
  );
}
