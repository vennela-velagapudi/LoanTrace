"use client";
import { useEffect, useState } from "react";
import Link from "next/link";
import { useRouter, usePathname } from "next/navigation";
import { getToken, getUserRole, getUsername, removeToken } from "@/lib/auth";
import { ChevronDown } from "lucide-react";

export default function ClientNav() {
  const [role, setRole] = useState<string | null>(null);
  const [username, setUsername] = useState<string | null>(null);
  const [dropdownOpen, setDropdownOpen] = useState(false);
  const router = useRouter();
  const pathname = usePathname();

  useEffect(() => {
    setRole(getUserRole());
    setUsername(getUsername());
    setDropdownOpen(false);
  }, [pathname]); // Re-check on route change

  const handleLogout = () => {
    removeToken();
    setRole(null);
    setUsername(null);
    router.push("/login");
  };

  const isDashboardRoute = pathname.startsWith("/operator") || pathname.startsWith("/reviewer") || pathname.startsWith("/consumer");

  return (
    <nav className="flex items-center gap-6 text-sm text-[var(--muted-foreground)]">
      {!role && pathname !== "/login" && !isDashboardRoute && (
        <Link href="/login" className="px-4 py-2 rounded-md bg-secondary text-white hover:bg-[var(--accent)] transition-colors">Login</Link>
      )}
      
      {role && isDashboardRoute && (
        <>
          
          <div className="relative ml-4 ">
            <button 
              onClick={() => setDropdownOpen(!dropdownOpen)} 
              className="flex items-center gap-1 text-slate-600 hover:text-slate-900 transition-colors cursor-pointer"
            >
              <span className="hidden sm:inline">Logged in as</span> <span className="font-bold text-slate-900 sm:ml-1 capitalize">{username}</span> <ChevronDown className="w-4 h-4 ml-1" />
            </button>
            
            {dropdownOpen && (
              <div className="absolute right-0 mt-2 w-48 bg-white border border-slate-200 rounded-md shadow-lg py-1 z-50 overflow-hidden">
                <Link 
                  href="/settings/security" 
                  className="block px-4 py-2 text-sm text-slate-700 hover:bg-slate-50 transition-colors cursor-pointer"
                  onClick={() => setDropdownOpen(false)}
                >
                  Security Settings
                </Link>
                <div className="border-t border-slate-100 my-1"></div>
                <button 
                  onClick={() => { setDropdownOpen(false); handleLogout(); }} 
                  className="w-full text-left px-4 py-2 text-sm text-red-600 hover:bg-red-50 transition-colors cursor-pointer"
                >
                  Logout
                </button>
              </div>
            )}
          </div>
        </>
      )}
    </nav>
  );
}
