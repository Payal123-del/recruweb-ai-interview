"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import { Bot, Shield, Building2, User, LogOut, ChevronRight, Sparkles } from "lucide-react";
import { ApiClient } from "@/lib/api";

export default function Navbar() {
  const router = useRouter();
  const [user, setUser] = useState<any>(null);

  useEffect(() => {
    const rawUser = localStorage.getItem("ardhnarishwar_user");
    if (rawUser) {
      try {
        setUser(JSON.parse(rawUser));
      } catch {}
    }
  }, []);

  const handleLogout = () => {
    ApiClient.clearToken();
    setUser(null);
    router.push("/login");
  };

  return (
    <header className="sticky top-0 z-50 w-full border-b border-slate-800 bg-slate-950/80 backdrop-blur-md">
      <div className="container mx-auto flex h-16 items-center justify-between px-4 sm:px-6">
        <Link href="/" className="flex items-center gap-3 group">
          <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-gradient-to-tr from-cyan-500 via-indigo-500 to-purple-600 shadow-lg shadow-indigo-500/20 group-hover:scale-105 transition-transform">
            <Bot className="h-6 w-6 text-white" />
          </div>
          <div>
            <span className="text-lg font-bold tracking-tight text-white flex items-center gap-1.5">
              Ardhnarishwar <span className="text-xs px-2 py-0.5 rounded-full bg-cyan-500/10 text-cyan-400 border border-cyan-500/30">AI Robotics</span>
            </span>
            <span className="text-[10px] text-slate-400 block -mt-1 tracking-wider uppercase">Enterprise Interview SaaS</span>
          </div>
        </Link>

        <nav className="flex items-center gap-4">
          {!user ? (
            <div className="flex items-center gap-3">
              <Link
                href="/login"
                className="text-sm font-medium text-slate-300 hover:text-white px-3 py-2 transition-colors"
              >
                Sign In
              </Link>
              <Link
                href="/candidate/interview/apex-demo-token-marcus-vance-2026"
                className="hidden sm:inline-flex items-center gap-1.5 text-xs font-semibold px-3.5 py-2 rounded-lg bg-slate-800 text-cyan-400 hover:bg-slate-700 border border-slate-700 transition-colors"
              >
                <Sparkles className="h-3.5 w-3.5" /> Demo Assessment
              </Link>
              <Link
                href="/login"
                className="inline-flex items-center gap-1 text-sm font-semibold px-4 py-2 rounded-lg bg-gradient-to-r from-indigo-500 to-cyan-500 hover:from-indigo-600 hover:to-cyan-600 text-white shadow-md shadow-indigo-500/20 transition-all hover:scale-[1.02]"
              >
                Launch App <ChevronRight className="h-4 w-4" />
              </Link>
            </div>
          ) : (
            <div className="flex items-center gap-3">
              {user.role === "SUPER_ADMIN" ? (
                <Link
                  href="/admin"
                  className="flex items-center gap-1.5 text-xs font-semibold px-3 py-1.5 rounded-lg bg-purple-500/10 text-purple-400 border border-purple-500/30"
                >
                  <Shield className="h-3.5 w-3.5" /> Super Admin Portal
                </Link>
              ) : (
                <Link
                  href="/company"
                  className="flex items-center gap-1.5 text-xs font-semibold px-3 py-1.5 rounded-lg bg-cyan-500/10 text-cyan-400 border border-cyan-500/30"
                >
                  <Building2 className="h-3.5 w-3.5" /> {user.company_name || "Company Workspace"}
                </Link>
              )}

              <div className="flex items-center gap-2 pl-3 border-l border-slate-800">
                <div className="text-right hidden sm:block">
                  <div className="text-xs font-medium text-white">{user.full_name}</div>
                  <div className="text-[10px] text-slate-400">{user.email}</div>
                </div>
                <button
                  onClick={handleLogout}
                  title="Logout"
                  className="p-2 rounded-lg text-slate-400 hover:text-red-400 hover:bg-slate-900 border border-transparent hover:border-slate-800 transition-colors"
                >
                  <LogOut className="h-4 w-4" />
                </button>
              </div>
            </div>
          )}
        </nav>
      </div>
    </header>
  );
}
