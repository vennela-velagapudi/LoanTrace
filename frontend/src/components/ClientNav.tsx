"use client";
import { useEffect, useState } from "react";
import Link from "next/link";
import { useRouter, usePathname } from "next/navigation";
import { getToken, getUserRole, getUsername, removeToken } from "@/lib/auth";

export default function ClientNav() {
  const [role, setRole] = useState<string | null>(null);
  const [username, setUsername] = useState<string | null>(null);
  const router = useRouter();
  const pathname = usePathname();

  useEffect(() => {
    setRole(getUserRole());
    setUsername(getUsername());
  }, [pathname]); // Re-check on route change

  const handleLogout = () => {
    removeToken();
    setRole(null);
    setUsername(null);
    router.push("/login");
  };

  return (
    <nav className="flex items-center gap-6 text-sm text-[var(--muted-foreground)]">
      {!role && (
        <>
          <Link href="/login" className="px-4 py-2 rounded-md bg-secondary text-white hover:bg-[var(--accent)] transition-colors">Login</Link>
        </>
      )}
      {role && (
        <>
          {role === "DATA_OPERATOR" && <Link href="/operator" className="hover:text-white transition-colors">Operator</Link>}
          {role === "REVIEWER" && <Link href="/reviewer" className="hover:text-white transition-colors">Reviewer Queue</Link>}
          {role === "DATA_CONSUMER" && <Link href="/consumer" className="hover:text-white transition-colors">Verified Records</Link>}
          
          <div className="flex items-center gap-4 ml-4 border-l border-[var(--border)] pl-4">
            <span className="text-white text-xs">Logged in as <span className="font-bold text-[var(--primary)]">{username}</span></span>
            <button onClick={handleLogout} className="px-4 py-2 rounded-md bg-red-950/50 text-red-200 hover:bg-red-900/50 transition-colors">Logout</button>
          </div>
        </>
      )}
    </nav>
  );
}
