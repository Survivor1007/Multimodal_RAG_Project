export interface LatencyBreakdown {
  query_expansion: number;
  text_embedding: number;
  faiss_dense_search: number;
  bm25_sparse_search: number;
  clip_vision_search: number;
  rrf_fusion: number;
  tavily_web_search: number;
  cross_encoder_rerank: number;
  llm_generation: number;
  total_backend_latency: number;
}

export interface ScoreBreakdown {
  faiss_similarity: number | null;
  bm25_score: number | null;
  clip_similarity: number | null;
  rrf_score: number | null;
  rerank_score: number | null;
}

export interface RankPositions {
  faiss: number | null;
  bm25: number | null;
  clip: number | null;
}

export interface SearchResult {
  chunk_id: number;
  content: string;
  score: number;
  chunk_type: string;
  metadata: Record<string, any>;
  scores?: ScoreBreakdown;
  ranks?: RankPositions;
}

export interface SearchRequest {
  query: string;
  k: number;
  use_reranker: boolean;
}

export interface SearchResponse {
  query: string;
  results: SearchResult[];
  total_retrieved: number;
  ranking_method: string;
  latency_ms: LatencyBreakdown;
}

export interface RAGRequest {
  query: string;
  k: number;
  use_reranker: boolean;
  temperature?: number;
  max_tokens?: number;
  use_web_search?: boolean;
}

export interface RAGResponse {
  query: string;
  answer: string;
  sources: SearchResult[];
  confidence: number;
  used_web_search: boolean;
  latency_ms: LatencyBreakdown;
}

export interface DocumentItem {
  id: number;
  filename: string;
  file_type: string;
  file_size: number;
  chunk_count: number;
  created_at: string;
}

export interface DocumentChunksResponse {
  document_id: number;
  chunk_count: number;
  chunks: {
    chunk_id: number;
    chunk_index: number;
    content: string;
    metadata: Record<string, any>;
  }[];
}

export interface MetricData {
  mrr_at_10: number;
  ndcg_at_10: number;
  recall_at_5: number;
  precision_at_5: number;
  avg_latency_ms: number;
}

export interface AnalyticsData {
  dataset_name: string;
  eval_samples: number;
  metrics: {
    bm25_only: MetricData;
    faiss_dense_baseline: MetricData;
    base_hybrid_rrf: MetricData;
    fine_tuned_hybrid_reranker: MetricData;
  };
  highlights: string[];
}