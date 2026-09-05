# 📡 Backend REST API Documentation

Complete REST API specification for the **Multimodal Hybrid RAG Backend**.

---

## Base URLs
* Local API V1: `http://localhost:8000/api/v1`
* Interactive OpenAPI Docs: `http://localhost:8000/docs`

---

## Core Endpoints Summary

| Endpoint | Method | Description |
| :--- | :--- | :--- |
| `/api/v1/search/search` | `POST` | Execute hybrid search (FAISS + BM25 + CLIP + RRF + Reranker) with full per-step latency metrics. |
| `/api/v1/rag/rag` | `POST` | Execute end-to-end RAG pipeline with Groq generation and adaptive Tavily search fallback. |
| `/api/v1/ingest/file` | `POST` | Ingest TXT, PDF, or DOCX documents into FAISS and BM25 vector stores. |
| `/api/v1/ingest/image` | `POST` | Ingest visual media into CLIP multimodal FAISS vector store. |
| `/api/v1/documents/list` | `GET` | Fetch all ingested documents, chunk counts, and metadata. |
| `/api/v1/documents/{doc_id}/chunks` | `GET` | Inspect chunk breakdown for a specific document. |
| `/api/v1/analytics/telemetry` | `GET` | Fetch system latency distribution, query log history, and evaluation metrics. |
| `/api/v1/analytics/eval-benchmark` | `GET` | Return baseline vs. fine-tuned retrieval benchmark metrics. |

---

## Sample Payloads

### 1. Hybrid Search Payload (`POST /api/v1/search/search`)

#### Request:
```json
{
  "query": "What is Reciprocal Rank Fusion?",
  "k": 5,
  "use_reranker": true,
  "use_web_search": false
}
```

#### Response:
```json
{
  "query": "What is Reciprocal Rank Fusion?",
  "results": [
    {
      "chunk_id": 14,
      "content": "Reciprocal Rank Fusion (RRF) is an algorithm that evaluates position ranks across multiple search algorithms...",
      "score": 0.912,
      "scores": {
        "faiss_similarity": 0.84,
        "bm25_score": 12.4,
        "clip_similarity": 0.0,
        "rrf_score": 0.032,
        "rerank_score": 0.94
      },
      "ranks": {
        "faiss": 1,
        "bm25": 2
      },
      "metadata": {
        "filename": "RAG_Overview.pdf",
        "file_type": "pdf"
      }
    }
  ],
  "latency_ms": {
    "query_expansion": 0.8,
    "text_embedding": 12.1,
    "faiss_dense_search": 2.4,
    "bm25_sparse_search": 1.9,
    "clip_vision_search": 0.0,
    "rrf_fusion": 0.5,
    "cross_encoder_rerank": 28.3,
    "total_backend_latency": 46.0
  }
}
```
