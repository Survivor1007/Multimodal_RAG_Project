import React, { useState } from "react";
import {
  Bot,
  User,
  Send,
  Sparkles,
  Clock,
  Globe,
  FileText,
  Activity,
  Layers,
} from "lucide-react";
import { searchApi } from "../api/searchApi";
import { type RAGResponse, type SearchResult, type LatencyBreakdown } from "../types/search";

interface ChatMessage {
  id: string;
  sender: "user" | "assistant";
  text: string;
  responseMeta?: RAGResponse;
}

export default function ChatPage() {
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      id: "1",
      sender: "assistant",
      text: "Hello! I am your Multimodal RAG Assistant. Ask me anything about your uploaded documents or search topics. I will use hybrid retrieval (FAISS + BM25 + CLIP + Reranking) and present per-step execution latency breakdown.",
    },
  ]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [useWebSearch, setUseWebSearch] = useState(false);
  const [activeTab, setActiveTab] = useState<"sources" | "latency">("sources");
  const [selectedMeta, setSelectedMeta] = useState<RAGResponse | null>(null);

  const handleSend = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || loading) return;

    const userMessage: ChatMessage = {
      id: Date.now().toString(),
      sender: "user",
      text: input,
    };

    setMessages((prev) => [...prev, userMessage]);
    setInput("");
    setLoading(true);

    try {
      const res = await searchApi.rag({
        query: userMessage.text,
        k: 5,
        use_reranker: true,
        use_web_search: useWebSearch,
      });

      const botMessage: ChatMessage = {
        id: (Date.now() + 1).toString(),
        sender: "assistant",
        text: res.answer,
        responseMeta: res,
      };

      setMessages((prev) => [...prev, botMessage]);
      setSelectedMeta(res);
    } catch (err: any) {
      const errorMessage: ChatMessage = {
        id: (Date.now() + 1).toString(),
        sender: "assistant",
        text: `Error processing query: ${err.message || "Backend connection failed"}`,
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 h-[calc(100vh-140px)]">
      {/* Left Chat Column */}
      <div className="lg:col-span-2 flex flex-col glass-panel overflow-hidden">
        {/* Chat Header */}
        <div className="p-4 border-b border-slate-200 dark:border-slate-800 flex items-center justify-between bg-white/50 dark:bg-slate-900/50">
          <div className="flex items-center gap-3">
            <div className="p-2 rounded-xl bg-brand-500/10 text-brand-600 dark:text-brand-400">
              <Bot className="w-5 h-5" />
            </div>
            <div>
              <h2 className="text-base font-bold text-slate-900 dark:text-white">RAG Assistant Chat</h2>
              <p className="text-xs text-slate-500">Groq LLM + Hybrid Retrieval Engine</p>
            </div>
          </div>

          {/* Web Search Toggle */}
          <button
            onClick={() => setUseWebSearch(!useWebSearch)}
            className={`flex items-center gap-2 px-3 py-1.5 rounded-lg text-xs font-semibold border transition-all ${
              useWebSearch
                ? "bg-indigo-500/10 text-indigo-600 dark:text-indigo-400 border-indigo-500/30"
                : "bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-400 border-slate-200 dark:border-slate-700"
            }`}
          >
            <Globe className="w-3.5 h-3.5" />
            <span>Force Web Fallback: {useWebSearch ? "ON" : "OFF"}</span>
          </button>
        </div>

        {/* Message History */}
        <div className="flex-1 overflow-y-auto p-4 space-y-4">
          {messages.map((msg) => (
            <div
              key={msg.id}
              className={`flex gap-3 ${msg.sender === "user" ? "justify-end" : "justify-start"}`}
            >
              {msg.sender === "assistant" && (
                <div className="p-2 rounded-xl bg-brand-600 text-white h-fit shadow-md">
                  <Bot className="w-4 h-4" />
                </div>
              )}

              <div
                className={`max-w-[80%] rounded-2xl p-4 space-y-2 text-sm ${
                  msg.sender === "user"
                    ? "bg-brand-600 text-white shadow-md"
                    : "bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 text-slate-800 dark:text-slate-200 shadow-sm"
                }`}
              >
                <p className="whitespace-pre-wrap leading-relaxed">{msg.text}</p>

                {msg.responseMeta && (
                  <div className="pt-2 border-t border-slate-200/60 dark:border-slate-800/60 flex flex-wrap items-center justify-between gap-2 text-xs">
                    <div className="flex items-center gap-1.5 font-semibold text-emerald-600 dark:text-emerald-400">
                      <Sparkles className="w-3.5 h-3.5" />
                      <span>Confidence: {(msg.responseMeta.confidence * 100).toFixed(0)}%</span>
                    </div>

                    <button
                      onClick={() => setSelectedMeta(msg.responseMeta!)}
                      className="text-brand-600 dark:text-brand-400 hover:underline flex items-center gap-1 font-medium"
                    >
                      <Activity className="w-3.5 h-3.5" />
                      <span>View Latency Breakdown ({msg.responseMeta.latency_ms.total_backend_latency} ms)</span>
                    </button>
                  </div>
                )}
              </div>

              {msg.sender === "user" && (
                <div className="p-2 rounded-xl bg-slate-200 dark:bg-slate-800 text-slate-700 dark:text-slate-300 h-fit">
                  <User className="w-4 h-4" />
                </div>
              )}
            </div>
          ))}

          {loading && (
            <div className="flex gap-3 items-center text-slate-500 dark:text-slate-400 text-xs italic">
              <Clock className="w-4 h-4 animate-spin text-brand-500" />
              <span>Executing Hybrid Search & LLM Generation...</span>
            </div>
          )}
        </div>

        {/* Input Bar */}
        <form onSubmit={handleSend} className="p-4 border-t border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 flex gap-3">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Ask a question about your documents..."
            className="flex-1 px-4 py-3 rounded-xl bg-slate-100 dark:bg-slate-950 border border-slate-200 dark:border-slate-800 text-sm focus:outline-none focus:ring-2 focus:ring-brand-500 text-slate-900 dark:text-white placeholder-slate-400"
          />
          <button
            type="submit"
            disabled={loading || !input.trim()}
            className="px-5 py-3 rounded-xl bg-brand-600 hover:bg-brand-500 text-white font-medium text-sm transition-all disabled:opacity-50 flex items-center gap-2 shadow-md"
          >
            <span>Send</span>
            <Send className="w-4 h-4" />
          </button>
        </form>
      </div>

      {/* Right Drawer: Sources & Step-by-Step Latency Profiler */}
      <div className="glass-panel p-4 flex flex-col h-full overflow-hidden">
        {/* Drawer Tab Headers */}
        <div className="flex border-b border-slate-200 dark:border-slate-800 mb-4">
          <button
            onClick={() => setActiveTab("sources")}
            className={`flex-1 py-2.5 text-xs font-bold border-b-2 transition-colors flex items-center justify-center gap-2 ${
              activeTab === "sources"
                ? "border-brand-600 text-brand-600 dark:text-brand-400"
                : "border-transparent text-slate-500 hover:text-slate-700"
            }`}
          >
            <FileText className="w-3.5 h-3.5" />
            <span>Retrieved Sources ({selectedMeta?.sources.length || 0})</span>
          </button>

          <button
            onClick={() => setActiveTab("latency")}
            className={`flex-1 py-2.5 text-xs font-bold border-b-2 transition-colors flex items-center justify-center gap-2 ${
              activeTab === "latency"
                ? "border-brand-600 text-brand-600 dark:text-brand-400"
                : "border-transparent text-slate-500 hover:text-slate-700"
            }`}
          >
            <Activity className="w-3.5 h-3.5" />
            <span>Per-Step Latency Profiler</span>
          </button>
        </div>

        {/* Drawer Content */}
        <div className="flex-1 overflow-y-auto space-y-4 pr-1">
          {!selectedMeta ? (
            <div className="text-center py-12 text-slate-400 text-xs space-y-2">
              <Layers className="w-8 h-8 mx-auto opacity-50" />
              <p>Ask a question in chat to view source scores and step-by-step latency profiling.</p>
            </div>
          ) : activeTab === "sources" ? (
            <div className="space-y-3">
              {selectedMeta.sources.map((source, i) => (
                <div key={i} className="p-3 rounded-xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 space-y-2">
                  <div className="flex items-center justify-between text-xs">
                    <span className="font-semibold text-brand-600 dark:text-brand-400">
                      {source.metadata.filename || source.metadata.title || `Chunk #${source.chunk_id}`}
                    </span>
                    <span className="px-2 py-0.5 rounded-full bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-300 font-mono text-[10px]">
                      Score: {source.score.toFixed(4)}
                    </span>
                  </div>

                  <p className="text-xs text-slate-600 dark:text-slate-300 line-clamp-3 font-mono bg-slate-50 dark:bg-slate-950 p-2 rounded-lg border border-slate-200/50 dark:border-slate-800/50">
                    {source.content}
                  </p>

                  {/* Score Breakdown Pills */}
                  {source.scores && (
                    <div className="flex flex-wrap gap-1.5 pt-1 text-[10px] font-mono">
                      {source.scores.faiss_similarity !== null && (
                        <span className="px-2 py-0.5 rounded bg-blue-500/10 text-blue-600 dark:text-blue-400">
                          FAISS: {source.scores.faiss_similarity.toFixed(2)}
                        </span>
                      )}
                      {source.scores.bm25_score !== null && (
                        <span className="px-2 py-0.5 rounded bg-amber-500/10 text-amber-600 dark:text-amber-400">
                          BM25: {source.scores.bm25_score.toFixed(2)}
                        </span>
                      )}
                      {source.scores.rerank_score !== null && (
                        <span className="px-2 py-0.5 rounded bg-purple-500/10 text-purple-600 dark:text-purple-400">
                          Rerank: {source.scores.rerank_score.toFixed(2)}
                        </span>
                      )}
                    </div>
                  )}
                </div>
              ))}
            </div>
          ) : (
            /* Latency Profiler View */
            <div className="space-y-4">
              <div className="p-3 rounded-xl bg-slate-100 dark:bg-slate-900 border border-slate-200 dark:border-slate-800 space-y-1">
                <div className="text-xs font-semibold text-slate-500">Total Backend Execution Time</div>
                <div className="text-2xl font-extrabold text-brand-600 dark:text-brand-400 font-mono">
                  {selectedMeta.latency_ms.total_backend_latency} ms
                </div>
              </div>

              {/* Waterfall Bar Charts */}
              <div className="space-y-3 text-xs">
                {[
                  { label: "Query Preprocessing", key: "query_expansion" as keyof LatencyBreakdown, color: "bg-blue-500" },
                  { label: "Dense Text Embedding", key: "text_embedding" as keyof LatencyBreakdown, color: "bg-indigo-500" },
                  { label: "FAISS Vector Search", key: "faiss_dense_search" as keyof LatencyBreakdown, color: "bg-emerald-500" },
                  { label: "BM25 Keyword Search", key: "bm25_sparse_search" as keyof LatencyBreakdown, color: "bg-amber-500" },
                  { label: "CLIP Vision Search", key: "clip_vision_search" as keyof LatencyBreakdown, color: "bg-cyan-500" },
                  { label: "Reciprocal Rank Fusion", key: "rrf_fusion" as keyof LatencyBreakdown, color: "bg-teal-500" },
                  { label: "Tavily Web Fallback", key: "tavily_web_search" as keyof LatencyBreakdown, color: "bg-rose-500" },
                  { label: "Cross-Encoder Rerank", key: "cross_encoder_rerank" as keyof LatencyBreakdown, color: "bg-purple-500" },
                  { label: "Groq LLM Answer Gen", key: "llm_generation" as keyof LatencyBreakdown, color: "bg-brand-500" },
                ].map((stage, idx) => {
                  const val = selectedMeta.latency_ms[stage.key] || 0.0;
                  const total = selectedMeta.latency_ms.total_backend_latency || 1.0;
                  const pct = Math.min(100, Math.max(2, (val / total) * 100));

                  return (
                    <div key={idx} className="space-y-1">
                      <div className="flex justify-between text-slate-700 dark:text-slate-300 font-medium">
                        <span>{stage.label}</span>
                        <span className="font-mono text-slate-500">{val} ms</span>
                      </div>
                      <div className="w-full h-2 rounded-full bg-slate-200 dark:bg-slate-800 overflow-hidden">
                        <div
                          className={`h-full ${stage.color} rounded-full transition-all duration-500`}
                          style={{ width: `${pct}%` }}
                        />
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
