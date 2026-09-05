import React, { useState } from "react";
import { Link } from "react-router-dom";
import {
  Bot,
  Sparkles,
  Zap,
  Search,
  BrainCircuit,
  ArrowRight,
  Clock,
  Database,
  Sliders,
} from "lucide-react";
import { searchApi } from "../api/searchApi";
import { type SearchResponse } from "../types/search";

export default function HomePage() {
  const [query, setQuery] = useState("");
  const [loading, setLoading] = useState(false);
  const [searchResponse, setSearchResponse] = useState<SearchResponse | null>(null);

  const handleQuickSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!query.trim()) return;

    setLoading(true);
    try {
      const res = await searchApi.search({
        query,
        k: 3,
        use_reranker: true,
      });
      setSearchResponse(res);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const featureCards = [
    {
      title: "Hybrid Retrieval Engine",
      desc: "Combines FAISS dense semantic search, BM25 sparse keyword matching, and CLIP multimodal vision vectors.",
      icon: Database,
      color: "from-blue-500 to-indigo-600",
    },
    {
      title: "Microsecond Latency Profiler",
      desc: "Instruments every execution stage (embeddings, vector search, RRF fusion, reranking, LLM) and sends breakdown telemetry to UI.",
      icon: Clock,
      color: "from-amber-500 to-orange-600",
    },
    {
      title: "Explainable Ranking Engine",
      desc: "Exposes raw FAISS, BM25, CLIP, RRF ranks, and Cross-Encoder relevance scores for transparent debugging.",
      icon: Sliders,
      color: "from-purple-500 to-pink-600",
    },
    {
      title: "CPU-Friendly Fine-Tuning",
      desc: "Contrastive learning fine-tuning pipeline for sentence-transformers and rerankers executable on standard laptop hardware.",
      icon: BrainCircuit,
      color: "from-emerald-500 to-teal-600",
    },
  ];

  return (
    <div className="space-y-16 py-4">
      {/* Hero Section */}
      <section className="relative overflow-hidden rounded-3xl bg-gradient-to-b from-brand-500/10 via-slate-100/50 to-white dark:from-brand-950/40 dark:via-slate-900/60 dark:to-slate-950 border border-slate-200/80 dark:border-slate-800/80 p-8 sm:p-12 text-center">
        <div className="max-w-3xl mx-auto space-y-6">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-brand-500/10 dark:bg-brand-400/10 border border-brand-500/20 text-brand-600 dark:text-brand-400 text-xs font-semibold">
            <Sparkles className="w-3.5 h-3.5" />
            <span>Multimodal Semantic Search & Production RAG Engine</span>
          </div>

          <h1 className="text-4xl sm:text-6xl font-extrabold tracking-tight bg-gradient-to-r from-slate-900 via-brand-600 to-indigo-600 dark:from-white dark:via-brand-300 dark:to-indigo-300 bg-clip-text text-transparent">
            Hybrid Retrieval & Explainable RAG Architecture
          </h1>

          <p className="text-lg text-slate-600 dark:text-slate-300 leading-relaxed">
            A production-grade platform featuring <strong>FAISS Dense Search</strong>, <strong>BM25 Keyword Matching</strong>, <strong>CLIP Vision Retrieval</strong>, <strong>Reciprocal Rank Fusion</strong>, and per-step latency measurement.
          </p>

          {/* CTA Buttons */}
          <div className="flex flex-wrap items-center justify-center gap-4 pt-2">
            <Link
              to="/chat"
              className="flex items-center gap-2 px-6 py-3 rounded-xl bg-gradient-to-r from-brand-600 to-indigo-600 hover:from-brand-500 hover:to-indigo-500 text-white font-semibold shadow-lg shadow-brand-500/25 transition-all hover:scale-105"
            >
              <Bot className="w-5 h-5" />
              <span>Launch RAG Assistant</span>
              <ArrowRight className="w-4 h-4" />
            </Link>

            <Link
              to="/documents"
              className="flex items-center gap-2 px-6 py-3 rounded-xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 text-slate-800 dark:text-slate-200 hover:bg-slate-100 dark:hover:bg-slate-800 font-semibold transition-all"
            >
              <Database className="w-5 h-5 text-indigo-500" />
              <span>Ingest Documents</span>
            </Link>

            <Link
              to="/analytics"
              className="flex items-center gap-2 px-6 py-3 rounded-xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 text-slate-800 dark:text-slate-200 hover:bg-slate-100 dark:hover:bg-slate-800 font-semibold transition-all"
            >
              <BrainCircuit className="w-5 h-5 text-emerald-500" />
              <span>View Fine-Tuning Benchmarks</span>
            </Link>
          </div>
        </div>
      </section>

      {/* Feature Highlights Grid */}
      <section className="space-y-6">
        <div className="text-center space-y-2">
          <h2 className="text-3xl font-bold tracking-tight text-slate-900 dark:text-white">
            Engineered for Retrieval Quality & Transparency
          </h2>
          <p className="text-slate-500 dark:text-slate-400">
            Overcoming standard single-retriever limitations through hybrid rank fusion and latency profiling.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {featureCards.map((card, idx) => {
            const Icon = card.icon;
            return (
              <div key={idx} className="glass-card p-6 space-y-4">
                <div className={`p-3 rounded-xl bg-gradient-to-tr ${card.color} text-white w-fit shadow-md`}>
                  <Icon className="w-6 h-6" />
                </div>
                <h3 className="text-lg font-bold text-slate-900 dark:text-white">{card.title}</h3>
                <p className="text-sm text-slate-600 dark:text-slate-400 leading-relaxed">{card.desc}</p>
              </div>
            );
          })}
        </div>
      </section>

      {/* Live Interactive Sandbox Preview */}
      <section className="glass-panel p-8 space-y-6">
        <div className="flex items-center gap-3 border-b border-slate-200 dark:border-slate-800 pb-4">
          <div className="p-2.5 rounded-xl bg-brand-500/10 text-brand-600 dark:text-brand-400">
            <Zap className="w-5 h-5" />
          </div>
          <div>
            <h3 className="text-xl font-bold text-slate-900 dark:text-white">Interactive Hybrid Search Sandbox</h3>
            <p className="text-xs text-slate-500 dark:text-slate-400">
              Query FAISS + BM25 + CLIP in real-time to inspect per-step execution latency.
            </p>
          </div>
        </div>

        <form onSubmit={handleQuickSearch} className="flex gap-3">
          <div className="relative flex-1">
            <Search className="absolute left-3.5 top-3.5 w-5 h-5 text-slate-400" />
            <input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="e.g. What is Reciprocal Rank Fusion?"
              className="w-full pl-11 pr-4 py-3 rounded-xl bg-slate-100 dark:bg-slate-900 border border-slate-200 dark:border-slate-800 focus:outline-none focus:ring-2 focus:ring-brand-500 text-slate-900 dark:text-white placeholder-slate-400 text-sm"
            />
          </div>
          <button
            type="submit"
            disabled={loading}
            className="px-6 py-3 rounded-xl bg-brand-600 hover:bg-brand-500 text-white font-medium text-sm transition-all disabled:opacity-50 flex items-center gap-2"
          >
            {loading ? <Clock className="w-4 h-4 animate-spin" /> : "Run Search"}
          </button>
        </form>

        {searchResponse && (
          <div className="space-y-4 pt-2">
            <div className="flex flex-wrap items-center justify-between gap-2 p-3 rounded-xl bg-slate-100/70 dark:bg-slate-900/70 border border-slate-200 dark:border-slate-800 text-xs font-mono">
              <span className="text-emerald-600 dark:text-emerald-400 font-semibold">
                Total Latency: {searchResponse.latency_ms.total_backend_latency} ms
              </span>
              <span className="text-slate-500">
                FAISS: {searchResponse.latency_ms.faiss_dense_search} ms | BM25: {searchResponse.latency_ms.bm25_sparse_search} ms | Rerank: {searchResponse.latency_ms.cross_encoder_rerank} ms
              </span>
            </div>

            <div className="space-y-3">
              {searchResponse.results.map((item, i) => (
                <div key={i} className="p-4 rounded-xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 space-y-2">
                  <div className="flex items-center justify-between text-xs text-slate-500">
                    <span className="font-semibold text-brand-600 dark:text-brand-400">Chunk #{item.chunk_id}</span>
                    <span className="px-2 py-0.5 rounded-full bg-brand-500/10 text-brand-600 dark:text-brand-400 font-mono">
                      Score: {item.score.toFixed(4)}
                    </span>
                  </div>
                  <p className="text-sm text-slate-700 dark:text-slate-300 line-clamp-2 font-mono bg-slate-50 dark:bg-slate-950 p-2.5 rounded-lg border border-slate-200/50 dark:border-slate-800/50">
                    {item.content}
                  </p>
                </div>
              ))}
            </div>
          </div>
        )}
      </section>

      {/* Architecture Tech Stack */}
      <section className="glass-panel p-8 space-y-6">
        <h3 className="text-xl font-bold text-slate-900 dark:text-white text-center">Tech Stack & Infrastructure</h3>
        <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-6 gap-4 text-center">
          {["FastAPI", "FAISS", "RankBM25", "OpenAI CLIP", "Groq LLM", "React 19"].map((tech, idx) => (
            <div key={idx} className="p-3 rounded-xl bg-slate-100 dark:bg-slate-900 border border-slate-200 dark:border-slate-800 font-semibold text-xs text-slate-700 dark:text-slate-300">
              {tech}
            </div>
          ))}
        </div>
      </section>
    </div>
  );
}
