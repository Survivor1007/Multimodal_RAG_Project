import React, { useState, useEffect } from "react";
import {
  Upload,
  FileText,
  Trash2,
  Eye,
  Database,
  Search,
  CheckCircle2,
  Clock,
  File,
  Image as ImageIcon,
  X,
} from "lucide-react";
import { searchApi } from "../api/searchApi";
import { uploadApi } from "../api/uploadApi";
import { type DocumentItem, type SearchResponse } from "../types/search";

export default function DocumentsPage() {
  const [activeTab, setActiveTab] = useState<"documents" | "search">("documents");
  const [documents, setDocuments] = useState<DocumentItem[]>([]);
  const [loadingDocs, setLoadingDocs] = useState(false);
//   const [selectedDocId, setSelectedDocId] = useState<number | null>(null);
  const [chunksModalData, setChunksModalData] = useState<any | null>(null);

  // Upload State
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [uploading, setUploading] = useState(false);
  const [uploadMessage, setUploadMessage] = useState<string | null>(null);

  // Search Debugger State
  const [searchQuery, setSearchQuery] = useState("");
  const [kCount, setKCount] = useState(5);
  const [useReranker, setUseReranker] = useState(true);
  const [searching, setSearching] = useState(false);
  const [searchResults, setSearchResults] = useState<SearchResponse | null>(null);

  const fetchDocuments = async () => {
    setLoadingDocs(true);
    try {
      const data = await searchApi.getDocuments();
      setDocuments(data.documents);
    } catch (err) {
      console.error(err);
    } finally {
      setLoadingDocs(false);
    }
  };

  useEffect(() => {
    fetchDocuments();
  }, []);

  const handleFileUpload = async (e: React.SubmitEvent) => {
    e.preventDefault();
    if (!selectedFile) return;

    setUploading(true);
    setUploadMessage(null);

    const formData = new FormData();
    formData.append("file", selectedFile);

    try {
      if (selectedFile.type.startsWith("image/")) {
        await uploadApi.uploadImage(formData);
      } else {
        await uploadApi.uploadFile(formData);
      }
      setUploadMessage(`Successfully ingested '${selectedFile.name}'!`);
      setSelectedFile(null);
      fetchDocuments();
    } catch (err: any) {
      setUploadMessage(`Ingestion failed: ${err.message || "Unknown error"}`);
    } finally {
      setUploading(false);
    }
  };

  const handleDelete = async (docId: number) => {
    if (!window.confirm("Are you sure you want to delete this document and its chunks?")) return;
    try {
      await searchApi.deleteDocument(docId);
      fetchDocuments();
    } catch (err: any) {
      alert(`Failed to delete document: ${err.message}`);
    }
  };

  const handleInspectChunks = async (docId: number) => {
    // setSelectedDocId(docId);
    try {
      const data = await searchApi.getDocumentChunks(docId);
      setChunksModalData(data);
    } catch (err: any) {
      alert(`Failed to fetch chunks: ${err.message}`);
    }
  };

  const handleDebugSearch = async (e: React.SubmitEvent) => {
    e.preventDefault();
    if (!searchQuery.trim()) return;

    setSearching(true);
    try {
      const res = await searchApi.search({
        query: searchQuery,
        k: kCount,
        use_reranker: useReranker,
      });
      setSearchResults(res);
    } catch (err: any) {
      alert(`Search error: ${err.message}`);
    } finally {
      setSearching(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Top Header & Tab Toggle */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 glass-panel p-6">
        <div>
          <h1 className="text-2xl font-extrabold text-slate-900 dark:text-white">Documents & Hybrid Search</h1>
          <p className="text-sm text-slate-500">Ingest multimodal files, inspect FAISS/BM25 chunks, and debug hybrid search.</p>
        </div>

        <div className="flex items-center gap-2 p-1 bg-slate-100 dark:bg-slate-900 rounded-xl border border-slate-200 dark:border-slate-800">
          <button
            onClick={() => setActiveTab("documents")}
            className={`px-4 py-2 rounded-lg text-xs font-bold transition-all flex items-center gap-2 ${
              activeTab === "documents"
                ? "bg-white dark:bg-slate-800 text-brand-600 dark:text-brand-400 shadow-sm"
                : "text-slate-600 dark:text-slate-400"
            }`}
          >
            <Database className="w-4 h-4" />
            <span>Document Management ({documents.length})</span>
          </button>

          <button
            onClick={() => setActiveTab("search")}
            className={`px-4 py-2 rounded-lg text-xs font-bold transition-all flex items-center gap-2 ${
              activeTab === "search"
                ? "bg-white dark:bg-slate-800 text-brand-600 dark:text-brand-400 shadow-sm"
                : "text-slate-600 dark:text-slate-400"
            }`}
          >
            <Search className="w-4 h-4" />
            <span>Hybrid Search Debugger</span>
          </button>
        </div>
      </div>

      {activeTab === "documents" ? (
        <div className="space-y-6">
          {/* File Drag and Drop Upload Card */}
          <div className="glass-panel p-6 space-y-4">
            <h2 className="text-lg font-bold text-slate-900 dark:text-white flex items-center gap-2">
              <Upload className="w-5 h-5 text-brand-500" />
              <span>Ingest Multimodal Document / Image</span>
            </h2>

            <form onSubmit={handleFileUpload} className="space-y-4">
              <div className="border-2 border-dashed border-slate-300 dark:border-slate-800 rounded-2xl p-8 text-center hover:border-brand-500 transition-colors bg-slate-50/50 dark:bg-slate-900/50">
                <input
                  type="file"
                  id="file-upload"
                  accept=".pdf,.docx,.txt,image/*"
                  onChange={(e) => setSelectedFile(e.target.files?.[0] || null)}
                  className="hidden"
                />
                <label htmlFor="file-upload" className="cursor-pointer space-y-2 block">
                  <div className="p-3 rounded-full bg-brand-500/10 text-brand-600 dark:text-brand-400 w-fit mx-auto">
                    <Upload className="w-6 h-6" />
                  </div>
                  <div className="text-sm font-semibold text-slate-700 dark:text-slate-300">
                    {selectedFile ? selectedFile.name : "Click to choose PDF, DOCX, TXT, or Image"}
                  </div>
                  <p className="text-xs text-slate-500">Supports text extraction, token chunking, FAISS vector indexing, & CLIP embeddings</p>
                </label>
              </div>

              {uploadMessage && (
                <div className="p-3 rounded-xl bg-brand-500/10 border border-brand-500/20 text-xs font-semibold text-brand-600 dark:text-brand-400 flex items-center gap-2">
                  <CheckCircle2 className="w-4 h-4" />
                  <span>{uploadMessage}</span>
                </div>
              )}

              <button
                type="submit"
                disabled={!selectedFile || uploading}
                className="w-full py-3 rounded-xl bg-brand-600 hover:bg-brand-500 text-white font-semibold text-sm transition-all disabled:opacity-50 flex items-center justify-center gap-2 shadow-md"
              >
                {uploading ? (
                  <>
                    <Clock className="w-4 h-4 animate-spin" />
                    <span>Processing Ingestion & Vector Indexing...</span>
                  </>
                ) : (
                  <>
                    <Upload className="w-4 h-4" />
                    <span>Ingest File</span>
                  </>
                )}
              </button>
            </form>
          </div>

          {/* Ingested Documents List Table */}
          <div className="glass-panel overflow-hidden space-y-4 p-6">
            <h2 className="text-lg font-bold text-slate-900 dark:text-white flex items-center gap-2">
              <FileText className="w-5 h-5 text-indigo-500" />
              <span>Ingested Document Library</span>
            </h2>

            {loadingDocs ? (
              <div className="text-center py-8 text-slate-500 text-xs flex items-center justify-center gap-2">
                <Clock className="w-4 h-4 animate-spin text-brand-500" />
                <span>Loading documents...</span>
              </div>
            ) : documents.length === 0 ? (
              <div className="text-center py-12 text-slate-400 text-xs space-y-2">
                <File className="w-8 h-8 mx-auto opacity-50" />
                <p>No documents ingested yet. Upload a file above to populate the vector store.</p>
              </div>
            ) : (
              <div className="overflow-x-auto">
                <table className="w-full text-left text-xs text-slate-600 dark:text-slate-300">
                  <thead className="bg-slate-100 dark:bg-slate-900 uppercase font-bold text-slate-500 text-[10px]">
                    <tr>
                      <th className="p-3">ID</th>
                      <th className="p-3">Filename</th>
                      <th className="p-3">Type</th>
                      <th className="p-3">Size</th>
                      <th className="p-3">Chunks</th>
                      <th className="p-3">Ingested At</th>
                      <th className="p-3 text-right">Actions</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-200 dark:divide-slate-800">
                    {documents.map((doc) => (
                      <tr key={doc.id} className="hover:bg-slate-50/50 dark:hover:bg-slate-900/50">
                        <td className="p-3 font-mono font-semibold">#{doc.id}</td>
                        <td className="p-3 font-medium text-slate-900 dark:text-white flex items-center gap-2">
                          {doc.file_type === "image" ? <ImageIcon className="w-4 h-4 text-cyan-500" /> : <FileText className="w-4 h-4 text-indigo-500" />}
                          {doc.filename}
                        </td>
                        <td className="p-3">
                          <span className="px-2 py-0.5 rounded-full bg-slate-100 dark:bg-slate-800 font-mono text-[10px] uppercase">
                            {doc.file_type}
                          </span>
                        </td>
                        <td className="p-3 font-mono">{(doc.file_size / 1024).toFixed(1)} KB</td>
                        <td className="p-3 font-mono font-bold text-brand-600 dark:text-brand-400">{doc.chunk_count}</td>
                        <td className="p-3">{doc.created_at ? new Date(doc.created_at).toLocaleDateString() : "N/A"}</td>
                        <td className="p-3 text-right space-x-2">
                          <button
                            onClick={() => handleInspectChunks(doc.id)}
                            className="p-1.5 rounded-lg bg-brand-500/10 text-brand-600 dark:text-brand-400 hover:bg-brand-500/20"
                            title="Inspect Chunks"
                          >
                            <Eye className="w-4 h-4" />
                          </button>
                          <button
                            onClick={() => handleDelete(doc.id)}
                            className="p-1.5 rounded-lg bg-rose-500/10 text-rose-600 dark:text-rose-400 hover:bg-rose-500/20"
                            title="Delete Document"
                          >
                            <Trash2 className="w-4 h-4" />
                          </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        </div>
      ) : (
        /* Hybrid Search Debugger Tab */
        <div className="glass-panel p-6 space-y-6">
          <h2 className="text-lg font-bold text-slate-900 dark:text-white flex items-center gap-2">
            <Search className="w-5 h-5 text-brand-500" />
            <span>Hybrid Search & RRF Score Inspector</span>
          </h2>

          <form onSubmit={handleDebugSearch} className="space-y-4">
            <div className="flex gap-3">
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="Enter query to test hybrid retrieval..."
                className="flex-1 px-4 py-3 rounded-xl bg-slate-100 dark:bg-slate-950 border border-slate-200 dark:border-slate-800 text-sm focus:outline-none focus:ring-2 focus:ring-brand-500"
              />
              <button
                type="submit"
                disabled={searching || !searchQuery.trim()}
                className="px-6 py-3 rounded-xl bg-brand-600 hover:bg-brand-500 text-white font-medium text-sm transition-all disabled:opacity-50 flex items-center gap-2 shadow-md"
              >
                {searching ? <Clock className="w-4 h-4 animate-spin" /> : "Run Debug Search"}
              </button>
            </div>

            <div className="flex flex-wrap items-center gap-6 text-xs text-slate-600 dark:text-slate-400">
              <label className="flex items-center gap-2 cursor-pointer">
                <input
                  type="checkbox"
                  checked={useReranker}
                  onChange={(e) => setUseReranker(e.target.checked)}
                  className="rounded text-brand-600"
                />
                <span>Apply Cross-Encoder Reranking</span>
              </label>

              <div className="flex items-center gap-2">
                <span>Top K Candidates:</span>
                <select
                  value={kCount}
                  onChange={(e) => setKCount(Number(e.target.value))}
                  className="px-2 py-1 rounded-lg bg-slate-100 dark:bg-slate-900 border border-slate-200 dark:border-slate-800 text-xs"
                >
                  <option value={3}>3</option>
                  <option value={5}>5</option>
                  <option value={10}>10</option>
                </select>
              </div>
            </div>
          </form>

          {searchResults && (
            <div className="space-y-4 pt-4 border-t border-slate-200 dark:border-slate-800">
              <div className="flex items-center justify-between text-xs font-mono text-slate-500">
                <span>Found {searchResults.total_retrieved} candidates</span>
                <span className="text-emerald-500 font-bold">Latency: {searchResults.latency_ms.total_backend_latency} ms</span>
              </div>

              <div className="space-y-3">
                {searchResults.results.map((res, i) => (
                  <div key={i} className="p-4 rounded-xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 space-y-2">
                    <div className="flex items-center justify-between text-xs">
                      <span className="font-semibold text-brand-600 dark:text-brand-400">Chunk #{res.chunk_id}</span>
                      <span className="px-2 py-0.5 rounded-full bg-brand-500/10 text-brand-600 dark:text-brand-400 font-mono font-bold">
                        Final Score: {res.score.toFixed(4)}
                      </span>
                    </div>

                    <p className="text-xs text-slate-700 dark:text-slate-300 font-mono bg-slate-50 dark:bg-slate-950 p-3 rounded-lg border border-slate-200/50 dark:border-slate-800/50">
                      {res.content}
                    </p>

                    {res.scores && (
                      <div className="flex flex-wrap gap-2 text-[10px] font-mono pt-1">
                        {res.scores.faiss_similarity !== null && (
                          <span className="px-2 py-1 rounded bg-blue-500/10 text-blue-600 dark:text-blue-400">
                            FAISS Sim: {res.scores.faiss_similarity.toFixed(4)}
                          </span>
                        )}
                        {res.scores.bm25_score !== null && (
                          <span className="px-2 py-1 rounded bg-amber-500/10 text-amber-600 dark:text-amber-400">
                            BM25 Score: {res.scores.bm25_score.toFixed(4)}
                          </span>
                        )}
                        {res.scores.rerank_score !== null && (
                          <span className="px-2 py-1 rounded bg-purple-500/10 text-purple-600 dark:text-purple-400">
                            Reranker Logit: {res.scores.rerank_score.toFixed(4)}
                          </span>
                        )}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      {/* Chunk Inspection Modal */}
      {chunksModalData && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/60 backdrop-blur-sm">
          <div className="glass-panel max-w-2xl w-full max-h-[80vh] flex flex-col p-6 space-y-4">
            <div className="flex items-center justify-between border-b border-slate-200 dark:border-slate-800 pb-3">
              <h3 className="text-lg font-bold text-slate-900 dark:text-white">
                Document #{chunksModalData.document_id} Chunk Inspection ({chunksModalData.chunk_count} chunks)
              </h3>
              <button onClick={() => setChunksModalData(null)} className="p-1 rounded-lg hover:bg-slate-100 dark:hover:bg-slate-800">
                <X className="w-5 h-5 text-slate-500" />
              </button>
            </div>

            <div className="flex-1 overflow-y-auto space-y-3 pr-2">
              {chunksModalData.chunks.map((c: any) => (
                <div key={c.chunk_id} className="p-3 rounded-xl bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-800 space-y-1">
                  <div className="text-[10px] font-mono text-brand-600 dark:text-brand-400 font-bold">Chunk #{c.chunk_index}</div>
                  <p className="text-xs text-slate-700 dark:text-slate-300 font-mono whitespace-pre-wrap">{c.content}</p>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
