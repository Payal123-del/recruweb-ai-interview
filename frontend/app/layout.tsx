import type { Metadata } from "next";
import "./globals.css";
import Navbar from "@/components/Navbar";

export const metadata: Metadata = {
  title: "Ardhnarishwar AI — Enterprise Robotics Interview SaaS Platform",
  description: "Next-generation multi-tenant AI assessment platform for robotics, autonomous systems, and embedded engineering hiring.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className="dark">
      <body className="min-h-screen bg-[#090d16] text-slate-100 flex flex-col antialiased">
        <Navbar />
        <main className="flex-1 flex flex-col">{children}</main>
        <footer className="border-t border-slate-800/80 bg-slate-950/60 py-8 text-center text-xs text-slate-500">
          <div className="container mx-auto px-4 flex flex-col sm:flex-row items-center justify-between gap-4">
            <div>
              &copy; {new Date().getFullYear()} Ardhnarishwar AI Robotics SaaS. Multi-Tenant Protected Architecture.
            </div>
            <div className="flex gap-6 text-slate-400">
              <span className="hover:text-cyan-400 cursor-pointer">Security Whitepaper</span>
              <span className="hover:text-cyan-400 cursor-pointer">Internal AI v1 Engine</span>
              <span className="hover:text-cyan-400 cursor-pointer">Privacy & Isolation</span>
            </div>
          </div>
        </footer>
      </body>
    </html>
  );
}
