import time
from typing import List, Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from collections import defaultdict
import hashlib
import structlog

from ..db.repositories.base_repository import BaseRepository
from ..db.repositories.document_repository import DocumentRepository
from ..db.models.chunk import Chunk
from ..ml.retrieval.hybrid_retriever import HybridRetriever
from ..ml.ranking.rrf_ranker import RRF_Ranker
from ..ml.ranking.explainability import ExplainabilityModule
from ..utils.serializers import to_python_float, clean_numpy

logger = structlog.get_logger()


class QueryService:
    """Handles search and retrieval logic with per-step latency measurement."""

    def __init__(self):
        self.document_repo = DocumentRepository()
        self.chunk_repo = BaseRepository(Chunk)
        self.hybrid_retriever = HybridRetriever()
        self.reranker = RRF_Ranker()
        self.explain_module = ExplainabilityModule()

    async def search(
        self,
        db: AsyncSession,
        query: str,
        k: int = 5,
        use_reranker: bool = True,
        latency_tracker: Optional[Dict[str, float]] = None
    ) -> List[dict]:
        """Perform hybrid search and return enriched results with reliable sources and timing context."""
        if latency_tracker is None:
            latency_tracker = {}

        # ----------------------------------------------------
        # 1. Hybrid Retrieval Phase
        # ----------------------------------------------------
        ranked_results = await self.hybrid_retriever.retrieve(
            query, k=k * 4, latency_tracker=latency_tracker
        )

        if not ranked_results:
            return []

        chunk_ids = [r.chunk_id for r in ranked_results]

        # ----------------------------------------------------
        # 2. Database Fetch & Deduplication
        # ----------------------------------------------------
        raw_sources = await self.document_repo.get_chunks_with_documents_and_hashes(
            db, chunk_ids=chunk_ids
        )

        chunk_map = {s["chunk_id"]: s for s in raw_sources}
        doc_chunk_count: Dict[str, Any] = defaultdict(int)
        MAX_CHUNK_PER_DOC = 3

        seen_chunk_content: set[str] = set()
        candidates = []

        for r in ranked_results:
            chunk_id = r.chunk_id
            score = r.rrf_score

            source = chunk_map.get(chunk_id)
            if not source:
                continue

            doc_hash = source.get("document_content_hash", "")
            if doc_chunk_count[doc_hash] >= MAX_CHUNK_PER_DOC:
                continue
            doc_chunk_count[doc_hash] += 1

            normalized_content = " ".join(source["content"].lower().split())
            content_hash = hashlib.sha256(normalized_content.encode("utf-8")).hexdigest()

            if content_hash in seen_chunk_content:
                continue
            seen_chunk_content.add(content_hash)

            source["score"] = float(score)
            source["scores"] = {
                "faiss_similarity": to_python_float(r.faiss_score),
                "bm25_score": to_python_float(r.bm25_score),
                "clip_similarity": to_python_float(r.clip_score),
                "rrf_score": to_python_float(r.rrf_score),
                "rerank_score": None
            }
            source["ranks"] = {
                "faiss": r.ranks.get("faiss"),
                "bm25": r.ranks.get("bm25"),
                "clip": r.ranks.get("clip")
            }
            source["retrieval"] = {
                "retrievers_used": list(r.ranks.keys()),
                "rank_positions": clean_numpy(r.ranks),
            }

            candidates.append(source)

        # ----------------------------------------------------
        # 3. Cross-Encoder Reranking Phase
        # ----------------------------------------------------
        if use_reranker and candidates:
            t_rerank_start = time.perf_counter()
            rerank_input = [(c["chunk_id"], c["score"], c["content"]) for c in candidates]
            reranked = await self.explain_module.reranker.rerank(query, rerank_input[: k * 2])
            latency_tracker["cross_encoder_rerank"] = round((time.perf_counter() - t_rerank_start) * 1000, 2)

            rerank_map = {cid: score for cid, score, _ in reranked}
            for candidate in candidates:
                if candidate["chunk_id"] in rerank_map:
                    rerank_val = float(rerank_map[candidate["chunk_id"]])
                    candidate["scores"]["rerank_score"] = round(rerank_val, 4)
                    candidate["score"] = round(rerank_val, 4)

            candidates = sorted(candidates, key=lambda x: x["score"], reverse=True)
        else:
            latency_tracker["cross_encoder_rerank"] = 0.0

        final_results = candidates[:k]
        for item in final_results:
            item.pop("document_content_hash", None)

        return final_results