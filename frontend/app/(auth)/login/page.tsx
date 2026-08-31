"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { Bot, Lock, Mail, ArrowRight, Shield, Building2, AlertCircle, Loader2 } from "lucide-react";
import { ApiClient } from "@/lib/api";

export default function LoginPage() {
  const router = useRouter();
  const [email, setEmail] = useState("admin@ardhnarishwar.ai");
  const [password, setPassword] = useState("AdminSecurePassword123!");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      const res = await ApiClient.login(email, password);
      ApiClient.setTokens(res.data.access_token, res.data.refresh_token);

      // Fetch user profile to determine routing
      const profileRes = await ApiClient.getProfile();
      localStorage.setItem("ardhnarishwar_user", JSON.stringify(profileRes.data));

      if (profileRes.data.role === "SUPER_ADMIN") {
        router.push("/admin");
      } else {
        router.push("/company");
      }
    } catch (err: any) {
      setError(err.message || "Failed to authenticate. Please check your credentials.");
    } finally {
      setLoading(false);
    }
  };

  const selectPreset = (em: string, pass: string) => {
    setEmail(em);
    setPassword(pass);
    setError(null);
  };

  return (
    <div className="flex-1 flex items-center justify-center p-4 sm:p-6">
      <div className="w-full max-w-md">
        {/* Header */}
        <div className="text-center mb-8">
          <div className="inline-flex h-12 w-12 items-center justify-center rounded-2xl bg-gradient-to-tr from-cyan-500 to-indigo-600 shadow-lg shadow-indigo-500/20 mb-4">
            <Bot className="h-7 w-7 text-white" />
          </div>
          <h1 className="text-2xl font-bold text-white tracking-tight">Sign In to Platform</h1>
          <p className="text-sm text-slate-400 mt-1">Multi-tenant AI Assessment System</p>
        </div>

        {/* Demo Account Presets */}
        <div className="mb-6 p-3.5 rounded-2xl bg-slate-900/90 border border-slate-800">
          <div className="text-xs font-semibold text-slate-400 mb-2.5 flex items-center gap-1.5">
            <span>Quick Fill Demo Credentials:</span>
          </div>
          <div className="grid grid-cols-3 gap-2">
            <button
              type="button"
              onClick={() => selectPreset("admin@ardhnarishwar.ai", "AdminSecurePassword123!")}
              className="px-2.5 py-1.5 rounded-lg bg-purple-500/10 hover:bg-purple-500/20 border border-purple-500/30 text-purple-300 text-xs font-medium transition-colors"
            >
              Super Admin
            </button>
            <button
              type="button"
              onClick={() => selectPreset("recruiter@apexrobotics.io", "ApexSecurePass2026!")}
              className="px-2.5 py-1.5 rounded-lg bg-cyan-500/10 hover:bg-cyan-500/20 border border-cyan-500/30 text-cyan-300 text-xs font-medium transition-colors"
            >
              Apex Robotics
            </button>
            <button
              type="button"
              onClick={() => selectPreset("recruiter@bostoncyber.com", "BostonSecurePass2026!")}
              className="px-2.5 py-1.5 rounded-lg bg-indigo-500/10 hover:bg-indigo-500/20 border border-indigo-500/30 text-indigo-300 text-xs font-medium transition-colors"
            >
              Boston Cyber
            </button>
          </div>
        </div>

        {/* Login Card */}
        <div className="p-6 sm:p-8 rounded-3xl bg-slate-900/60 border border-slate-800 shadow-xl backdrop-blur-xl">
          {error && (
            <div className="mb-5 p-3.5 rounded-xl bg-red-500/10 border border-red-500/30 text-red-400 text-xs flex items-center gap-2.5">
              <AlertCircle className="h-4 w-4 shrink-0" />
              <span>{error}</span>
            </div>
          )}

          <form onSubmit={handleLogin} className="space-y-4">
            <div>
              <label className="block text-xs font-medium text-slate-300 mb-1.5">Work Email</label>
              <div className="relative">
                <Mail className="absolute left-3.5 top-1/2 -translate-y-1/2 h-4 w-4 text-slate-500" />
                <input
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  required
                  placeholder="name@company.com"
                  className="w-full pl-10 pr-4 py-2.5 rounded-xl bg-slate-950 border border-slate-800 focus:border-cyan-500 focus:outline-none text-sm text-white placeholder:text-slate-600 transition-colors"
                />
              </div>
            </div>

            <div>
              <label className="block text-xs font-medium text-slate-300 mb-1.5">Password</label>
              <div className="relative">
                <Lock className="absolute left-3.5 top-1/2 -translate-y-1/2 h-4 w-4 text-slate-500" />
                <input
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  required
                  placeholder="••••••••"
                  className="w-full pl-10 pr-4 py-2.5 rounded-xl bg-slate-950 border border-slate-800 focus:border-cyan-500 focus:outline-none text-sm text-white placeholder:text-slate-600 transition-colors"
                />
              </div>
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full mt-2 py-3 rounded-xl bg-gradient-to-r from-cyan-500 to-indigo-600 hover:from-cyan-400 hover:to-indigo-500 text-white font-semibold text-sm shadow-lg shadow-indigo-500/20 transition-all flex items-center justify-center gap-2 disabled:opacity-50"
            >
              {loading ? (
                <>
                  <Loader2 className="h-4 w-4 animate-spin" /> Verifying...
                </>
              ) : (
                <>
                  Sign In <ArrowRight className="h-4 w-4" />
                </>
              )}
            </button>
          </form>
        </div>
      </div>
    </div>
  );
}
