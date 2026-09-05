from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class LatencyBreakdown(BaseModel):
    query_expansion: float = Field(default=0.0, description="Time in ms for query expansion / rewriting")
    text_embedding: float = Field(default=0.0, description="Time in ms for dense text embedding generation")
    faiss_dense_search: float = Field(default=0.0, description="Time in ms for FAISS dense vector search")
    bm25_sparse_search: float = Field(default=0.0, description="Time in ms for BM25 keyword search")
    clip_vision_search: float = Field(default=0.0, description="Time in ms for CLIP vision vector search")
    rrf_fusion: float = Field(default=0.0, description="Time in ms for Reciprocal Rank Fusion")
    tavily_web_search: float = Field(default=0.0, description="Time in ms for Tavily web search fallback")
    cross_encoder_rerank: float = Field(default=0.0, description="Time in ms for Cross-Encoder reranking")
    llm_generation: float = Field(default=0.0, description="Time in ms for Groq LLM answer generation")
    total_backend_latency: float = Field(default=0.0, description="Total backend processing time in ms")


class ScoreBreakdown(BaseModel):
    faiss_similarity: Optional[float] = Field(default=None, description="FAISS cosine similarity")
    bm25_score: Optional[float] = Field(default=None, description="BM25 keyword relevance score")
    clip_similarity: Optional[float] = Field(default=None, description="CLIP vision vector similarity")
    rrf_score: Optional[float] = Field(default=None, description="Reciprocal Rank Fusion unified score")
    rerank_score: Optional[float] = Field(default=None, description="Cross-Encoder reranker relevance score")


class RankPositions(BaseModel):
    faiss: Optional[int] = Field(default=None, description="Rank in FAISS dense search")
    bm25: Optional[int] = Field(default=None, description="Rank in BM25 sparse search")
    clip: Optional[int] = Field(default=None, description="Rank in CLIP vision search")


class RetrievedChunk(BaseModel):
    chunk_id: int
    content: str
    score: float
    chunk_type: str = "text"
    metadata: Dict[str, Any] = Field(default_factory=dict)
    scores: Optional[ScoreBreakdown] = Field(default=None, description="Detailed score breakdown per channel")
    ranks: Optional[RankPositions] = Field(default=None, description="Rank positions per channel")


class SearchResponse(BaseModel):
    query: str
    results: List[RetrievedChunk]
    total_retrieved: int
    ranking_method: str = "hybrid_rrf_reranker"
    latency_ms: LatencyBreakdown = Field(default_factory=LatencyBreakdown)


class RAGResponse(BaseModel):
    query: str
    answer: str
    sources: List[RetrievedChunk]
    confidence: float = Field(..., ge=0.0, le=1.0)
    used_web_search: bool
    latency_ms: LatencyBreakdown = Field(default_factory=LatencyBreakdown)
