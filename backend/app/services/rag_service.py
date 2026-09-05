import time
from typing import List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
import asyncio

from groq import Groq
from tavily import TavilyClient

from .query_service import QueryService
from ..ml.ranking.explainability import ExplainabilityModule
from ..core.config import settings
from ..schemas.query import RAGRequest
from ..utils.serializers import clean_numpy


class RAGService:
    """Real RAG with Groq + Adaptive Tavily Web Search + Cross-Encoder + Timing Profiler."""

    def __init__(self):
        self.query_service = QueryService()
        self.explain_module = ExplainabilityModule()

        self.groq_client = Groq(api_key=settings.GROQ_API_KEY) if settings.GROQ_API_KEY else None
        self.tavily_client = TavilyClient(api_key=settings.TAVILY_API_KEY) if settings.TAVILY_API_KEY else None

    async def _get_web_search_results(self, query: str, max_results: int = 5) -> List[dict]:
        """Fetch real-time web results using Tavily."""
        if not self.tavily_client:
            return []

        try:
            response = await asyncio.to_thread(
                self.tavily_client.search,
                query=query,
                search_depth="basic",
                max_results=max_results,
                include_answer=True,
                include_raw_content=False,
            )

            results = []
            for i, item in enumerate(response.get("results", [])):
                url = item.get("url", "")
                results.append({
                    "chunk_id": -(i + 1),
                    "content": f"Title: {item.get('title', '')}\nSource: {url}\n\n{item.get('content', '')}",
                    "score": 0.90,
                    "chunk_type": "web",
                    "metadata": {
                        "source": "tavily",
                        "url": url,
                        "title": item.get("title", ""),
                    },
                })
            return results
        except Exception as e:
            print(f"Tavily error: {e}")
            return []

    async def generate_rag_response(self, db: AsyncSession, request: RAGRequest) -> Dict[str, Any]:
        """Adaptive RAG: Internal + Optional/Adaptive Tavily Web Search + Groq + Telemetry."""
        t_total_start = time.perf_counter()
        latency_tracker: Dict[str, float] = {
            "query_expansion": 0.0,
            "text_embedding": 0.0,
            "faiss_dense_search": 0.0,
            "bm25_sparse_search": 0.0,
            "clip_vision_search": 0.0,
            "rrf_fusion": 0.0,
            "tavily_web_search": 0.0,
            "cross_encoder_rerank": 0.0,
            "llm_generation": 0.0,
            "total_backend_latency": 0.0,
        }

        if not self.groq_client:
            return {
                "query": request.query,
                "answer": "Groq API key is not configured. Please add GROQ_API_KEY to backend/.env",
                "sources": [],
                "confidence": 0.0,
                "used_web_search": False,
                "latency_ms": latency_tracker,
            }

        # Step 1: Internal Hybrid Retrieval (FAISS + BM25 + RRF)
        internal_results = await self.query_service.search(
            db=db,
            query=request.query,
            k=request.k * 4,
            use_reranker=False,
            latency_tracker=latency_tracker,
        )

        # Step 2: Adaptive Web Search Decision
        should_use_web = request.use_web_search

        if not should_use_web and internal_results:
            top_internal_score = max(
                (r.get("score", 0.0) for r in internal_results), default=0.0
            )
            should_use_web = top_internal_score < settings.WEB_SEARCH_THRESHOLD

        web_results = []
        if should_use_web:
            t_web_start = time.perf_counter()
            web_results = await self._get_web_search_results(
                request.query, settings.TAVILY_MAX_RESULTS
            )
            latency_tracker["tavily_web_search"] = round((time.perf_counter() - t_web_start) * 1000, 2)
            print(f"🌐 Tavily Web Search triggered. Found {len(web_results)} results.")

        # Step 3: Combine Internal + Web results
        combined = internal_results + web_results
        seen = {}
        unique_candidates = []

        for item in combined:
            if item["chunk_id"] > 0:
                key = f"db_{item['chunk_id']}"
            else:
                key = f"web_{item['metadata'].get('url', item['content'][:100])}"

            if key not in seen:
                seen[key] = True
                unique_candidates.append({
                    "chunk_id": item["chunk_id"],
                    "score": float(item["score"]),
                    "content": item["content"],
                    "metadata": item.get("metadata", {}),
                    "scores": clean_numpy(item.get("scores", {})),
                    "ranks": clean_numpy(item.get("ranks", {})),
                    "retrieval": clean_numpy(item.get("retrieval", {})),
                })

        def is_relevant(query: str, content: str) -> bool:
            query_tokens = set(query.lower().split())
            content_tokens = set(content.lower().split())
            overlap = len(query_tokens & content_tokens)
            return overlap >= 1 or len(query_tokens) == 0

        filtered_candidates = [
            item for item in unique_candidates if is_relevant(request.query, item["content"])
        ]
        if not filtered_candidates:
            filtered_candidates = unique_candidates

        # Step 4: Cross-Encoder Reranking
        t_rerank_start = time.perf_counter()
        rerank_input = [
            (item["chunk_id"], item["score"], item["content"])
            for item in filtered_candidates
        ]
        reranked = await self.explain_module.reranker.rerank(
            request.query, rerank_input[: request.k * 2]
        )
        latency_tracker["cross_encoder_rerank"] = round((time.perf_counter() - t_rerank_start) * 1000, 2)

        # Step 5: Final sources
        final_sources = []
        for cid, score, content in reranked[: request.k]:
            original = next((item for item in combined if item["chunk_id"] == cid), None)

            final_sources.append({
                "chunk_id": cid,
                "content": content[:750] + "..." if len(content) > 750 else content,
                "score": float(score),
                "chunk_type": "web" if cid < 0 else "text",
                "metadata": original["metadata"] if original else {},
                "scores": clean_numpy(original.get("scores")) if original else None,
                "ranks": clean_numpy(original.get("ranks")) if original else None,
                "retrieval": clean_numpy(original.get("retrieval")) if original else None,
            })

        # Step 6: Generate answer with Groq
        context = "\n\n".join([s["content"] for s in final_sources])

        rerank_scores = [float(score) for _, score, _ in reranked[: request.k]]
        avg_rerank_score = sum(rerank_scores) / len(rerank_scores) if rerank_scores else 0.0
        normalized_rerank = max(0.0, min(1.0, avg_rerank_score))

        retrieval_scores = [item.get("score", 0.0) for item in final_sources if item["chunk_id"] > 0]
        avg_retrieval_score = sum(retrieval_scores) / len(retrieval_scores) if retrieval_scores else 0.0
        normalized_retrieval = max(0.0, min(1.0, avg_retrieval_score))

        coverage = min(1.0, len(final_sources) / max(1, request.k))
        web_penalty = 0.15 if should_use_web else 0.0

        confidence = (
            0.5 * normalized_rerank + 0.3 * normalized_retrieval + 0.2 * coverage
        ) - web_penalty
        confidence = max(0.0, min(1.0, confidence))

        t_llm_start = time.perf_counter()
        try:
            completion = await asyncio.to_thread(
                self.groq_client.chat.completions.create,
                model=settings.GROQ_MODEL,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a precise multimodal RAG assistant. Answer using only the provided context. Cite sources clearly.",
                    },
                    {"role": "user", "content": f"Context:\n{context}\n\nQuestion: {request.query}"},
                ],
                temperature=request.temperature,
                max_tokens=request.max_tokens,
            )
            answer = completion.choices[0].message.content.strip()
        except Exception as e:
            answer = f"Failed to generate response with Groq: {str(e)}"
            confidence = 0.45
        latency_tracker["llm_generation"] = round((time.perf_counter() - t_llm_start) * 1000, 2)

        latency_tracker["total_backend_latency"] = round((time.perf_counter() - t_total_start) * 1000, 2)

        return {
            "query": request.query,
            "answer": answer,
            "sources": final_sources,
            "confidence": float(confidence),
            "used_web_search": should_use_web,
            "latency_ms": latency_tracker,
        }