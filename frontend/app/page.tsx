import Link from "next/link";
import {
  Bot, ShieldCheck, Cpu, Building2, Zap, Award, Layers, Users,
  CheckCircle2, ArrowRight, Video, FileText, Database, Lock, BarChart3
} from "lucide-react";

export default function LandingPage() {
  return (
    <div className="flex-1 flex flex-col">
      {/* 1. Hero Section */}
      <section className="relative overflow-hidden pt-20 pb-28 md:pt-28 md:pb-36 border-b border-slate-800">
        <div className="absolute inset-0 bg-[radial-gradient(ellipse_80%_80%_at_50%_-20%,rgba(120,119,198,0.15),rgba(255,255,255,0))]" />
        <div className="container mx-auto px-4 relative z-10 text-center max-w-5xl">
          <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-slate-900 border border-slate-800 text-slate-300 text-xs font-medium mb-8">
            <span className="flex h-2 w-2 rounded-full bg-cyan-400 animate-pulse" />
            <span>Autonomous Robotics & AI Interview Engine v1.0 Live</span>
          </div>

          <h1 className="text-4xl sm:text-6xl md:text-7xl font-extrabold tracking-tight text-white mb-6 leading-tight">
            Next-Gen AI Assessments for{" "}
            <span className="bg-gradient-to-r from-cyan-400 via-indigo-400 to-purple-500 bg-clip-text text-transparent">
              Robotics & Hardware
            </span>{" "}
            Engineering
          </h1>

          <p className="text-lg sm:text-xl text-slate-400 max-w-3xl mx-auto mb-10 leading-relaxed font-normal">
            A commercial multi-tenant B2B SaaS platform for automated, unbiased technical screening. Conduct structured video interviews, evaluate kinematics, SLAM, and ROS2 competencies with our internal AI evaluation framework.
          </p>

          <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
            <Link
              href="/login"
              className="w-full sm:w-auto inline-flex items-center justify-center gap-2 px-7 py-3.5 rounded-xl bg-gradient-to-r from-cyan-500 to-indigo-600 hover:from-cyan-400 hover:to-indigo-500 text-white font-semibold shadow-lg shadow-indigo-500/25 transition-all hover:scale-105"
            >
              Access SaaS Portal <ArrowRight className="h-4 w-4" />
            </Link>
            <Link
              href="/candidate/interview/apex-demo-token-marcus-vance-2026"
              className="w-full sm:w-auto inline-flex items-center justify-center gap-2 px-7 py-3.5 rounded-xl bg-slate-900 hover:bg-slate-800 border border-slate-700 text-slate-200 font-medium transition-all"
            >
              <Video className="h-4 w-4 text-cyan-400" /> Experience Candidate UI
            </Link>
          </div>

          {/* Trust Highlights */}
          <div className="mt-16 grid grid-cols-2 md:grid-cols-4 gap-4 text-left">
            <div className="p-4 rounded-xl bg-slate-900/60 border border-slate-800">
              <div className="text-2xl font-bold text-white">100%</div>
              <div className="text-xs text-slate-400">Strict Tenant Data Isolation</div>
            </div>
            <div className="p-4 rounded-xl bg-slate-900/60 border border-slate-800">
              <div className="text-2xl font-bold text-cyan-400">0 ms</div>
              <div className="text-xs text-slate-400">3rd-Party LLM Dependency</div>
            </div>
            <div className="p-4 rounded-xl bg-slate-900/60 border border-slate-800">
              <div className="text-2xl font-bold text-indigo-400">Argon2id</div>
              <div className="text-xs text-slate-400">Cryptographic Auth & Tokens</div>
            </div>
            <div className="p-4 rounded-xl bg-slate-900/60 border border-slate-800">
              <div className="text-2xl font-bold text-purple-400">Automated</div>
              <div className="text-xs text-slate-400">PDF Report Generation</div>
            </div>
          </div>
        </div>
      </section>

      {/* 2. Platform Architecture Pillars */}
      <section className="py-20 bg-slate-950/40 border-b border-slate-800">
        <div className="container mx-auto px-4 max-w-6xl">
          <div className="text-center max-w-3xl mx-auto mb-16">
            <h2 className="text-xs font-bold uppercase tracking-widest text-cyan-400 mb-2">Core SaaS Architecture</h2>
            <p className="text-3xl font-bold text-white">Engineered for Global B2B Scale & Strict Isolation</p>
          </div>

          <div className="grid md:grid-cols-3 gap-8">
            <div className="p-6 rounded-2xl bg-slate-900/50 border border-slate-800 hover:border-slate-700 transition-colors">
              <div className="h-12 w-12 rounded-xl bg-cyan-500/10 border border-cyan-500/30 flex items-center justify-center text-cyan-400 mb-5">
                <Building2 className="h-6 w-6" />
              </div>
              <h3 className="text-lg font-semibold text-white mb-2">Multi-Tenant Isolation</h3>
              <p className="text-sm text-slate-400 leading-relaxed">
                Query-level scoping and scoped repositories ensure that Company A can never view, mutate, or query Company B&apos;s jobs, candidates, or interview video recordings.
              </p>
            </div>

            <div className="p-6 rounded-2xl bg-slate-900/50 border border-slate-800 hover:border-slate-700 transition-colors">
              <div className="h-12 w-12 rounded-xl bg-indigo-500/10 border border-indigo-500/30 flex items-center justify-center text-indigo-400 mb-5">
                <Cpu className="h-6 w-6" />
              </div>
              <h3 className="text-lg font-semibold text-white mb-2">Internal AI Engine v1.0</h3>
              <p className="text-sm text-slate-400 leading-relaxed">
                Modular architecture (QuestionSelector, AnswerAnalyzer, Technical & Behavioral Evaluator) running deterministic NLP rubrics without proprietary API keys.
              </p>
            </div>

            <div className="p-6 rounded-2xl bg-slate-900/50 border border-slate-800 hover:border-slate-700 transition-colors">
              <div className="h-12 w-12 rounded-xl bg-purple-500/10 border border-purple-500/30 flex items-center justify-center text-purple-400 mb-5">
                <Lock className="h-6 w-6" />
              </div>
              <h3 className="text-lg font-semibold text-white mb-2">Private Media & Single-Use Tokens</h3>
              <p className="text-sm text-slate-400 leading-relaxed">
                Candidate invitations use cryptographic single-use tokens. Video and audio streams are stored securely behind temporary signed HMAC URLs.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* 3. Demo Roles & Quick Launch */}
      <section className="py-20">
        <div className="container mx-auto px-4 max-w-5xl">
          <div className="p-8 sm:p-12 rounded-3xl bg-gradient-to-b from-slate-900 to-slate-950 border border-slate-800 text-center">
            <h2 className="text-2xl sm:text-3xl font-bold text-white mb-4">
              Explore Demo Portals Immediately
            </h2>
            <p className="text-sm sm:text-base text-slate-400 max-w-2xl mx-auto mb-8">
              Log in with pre-seeded enterprise credentials to experience the Super Admin control center or the Company Recruiter workspace.
            </p>

            <div className="grid sm:grid-cols-3 gap-4 text-left max-w-3xl mx-auto">
              <div className="p-4 rounded-xl bg-slate-950/80 border border-slate-800">
                <div className="text-xs font-semibold text-purple-400 mb-1">Super Admin</div>
                <div className="text-xs text-slate-300 font-mono">admin@ardhnarishwar.ai</div>
                <div className="text-[11px] text-slate-500 mt-1">Pass: AdminSecurePassword123!</div>
              </div>

              <div className="p-4 rounded-xl bg-slate-950/80 border border-slate-800">
                <div className="text-xs font-semibold text-cyan-400 mb-1">Tenant A: Apex Robotics</div>
                <div className="text-xs text-slate-300 font-mono">recruiter@apexrobotics.io</div>
                <div className="text-[11px] text-slate-500 mt-1">Pass: ApexSecurePass2026!</div>
              </div>

              <div className="p-4 rounded-xl bg-slate-950/80 border border-slate-800">
                <div className="text-xs font-semibold text-indigo-400 mb-1">Tenant B: Boston Cyber</div>
                <div className="text-xs text-slate-300 font-mono">recruiter@bostoncyber.com</div>
                <div className="text-[11px] text-slate-500 mt-1">Pass: BostonSecurePass2026!</div>
              </div>
            </div>

            <div className="mt-8">
              <Link
                href="/login"
                className="inline-flex items-center gap-2 px-8 py-3.5 rounded-xl bg-cyan-500 hover:bg-cyan-400 text-slate-950 font-bold shadow-lg shadow-cyan-500/20 transition-all hover:scale-105"
              >
                Go to Unified Sign In <ArrowRight className="h-4 w-4" />
              </Link>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
}
