import { Sparkles, Cpu, ShieldCheck } from "lucide-react";

export default function Footer() {
  return (
    <footer className="w-full border-t border-slate-200/80 dark:border-slate-800/80 bg-white/50 dark:bg-slate-950/50 py-8 transition-colors mt-auto">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex flex-col md:flex-row items-center justify-between gap-4">
          <div className="flex items-center gap-2 text-sm text-slate-500 dark:text-slate-400">
            <Sparkles className="w-4 h-4 text-brand-500" />
            <span>Multimodal Hybrid RAG Architecture & Performance Telemetry Engine</span>
          </div>

          <div className="flex items-center gap-4 text-xs text-slate-500 dark:text-slate-400">
            <div className="flex items-center gap-1.5 px-2.5 py-1 rounded-md bg-slate-100 dark:bg-slate-900 border border-slate-200 dark:border-slate-800">
              <Cpu className="w-3.5 h-3.5 text-indigo-500" />
              <span>FAISS + BM25 + CLIP + Cross-Encoder</span>
            </div>
            <div className="flex items-center gap-1.5 px-2.5 py-1 rounded-md bg-slate-100 dark:bg-slate-900 border border-slate-200 dark:border-slate-800">
              <ShieldCheck className="w-3.5 h-3.5 text-emerald-500" />
              <span>Production AI System</span>
            </div>
          </div>
        </div>
      </div>
    </footer>
  );
}
