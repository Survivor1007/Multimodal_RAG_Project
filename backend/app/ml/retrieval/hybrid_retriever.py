import time
from typing import List, Tuple, Dict, Optional
import numpy as np
import structlog

from .semantic_retriever import SemanticRetriever
from .keyword_retriever import KeywordRetriever
from ..embeddings.image_embedder import ImageEmbedder
from .faiss_manager import FAISSManager
from ..ranking.rrf_ranker import RRF_Ranker
from .retrieval_result import HybridResult

logger = structlog.get_logger()


class HybridRetriever:
    def __init__(self):
        self.semantic = SemanticRetriever()
        self.keyword = KeywordRetriever()
        self.image_embedder = ImageEmbedder()
        self.faiss_manager = FAISSManager()
        self.rrf_ranker = RRF_Ranker()

    async def retrieve(
        self,
        query: str,
        k: int = 10,
        latency_tracker: Optional[Dict[str, float]] = None
    ) -> List[HybridResult]:
        """
        Enhanced Hybrid Retriever with timing instrumentation, query intent classification,
        score normalization, and Reciprocal Rank Fusion.
        """
        if latency_tracker is None:
            latency_tracker = {}

        # ----------------------------------------------------
        # 1. Query Cleaning / Pre-processing
        # ----------------------------------------------------
        t0 = time.perf_counter()
        cleaned_query = " ".join(query.strip().split())
        latency_tracker["query_expansion"] = round((time.perf_counter() - t0) * 1000, 2)

        # ----------------------------------------------------
        # 2. Dense Semantic Search (FAISS + Embedder)
        # ----------------------------------------------------
        t_emb_start = time.perf_counter()
        # Embed text is triggered inside semantic.retrieve
        t_faiss_start = time.perf_counter()
        sem_results = await self.semantic.retrieve(cleaned_query, k * 2)
        t_faiss_end = time.perf_counter()

        latency_tracker["text_embedding"] = round((t_faiss_start - t_emb_start) * 1000, 2)
        latency_tracker["faiss_dense_search"] = round((t_faiss_end - t_faiss_start) * 1000, 2)

        # ----------------------------------------------------
        # 3. Sparse Keyword Search (BM25)
        # ----------------------------------------------------
        t_bm25_start = time.perf_counter()
        kw_results = await self.keyword.retrieve(cleaned_query, k * 2)
        latency_tracker["bm25_sparse_search"] = round((time.perf_counter() - t_bm25_start) * 1000, 2)

        # ----------------------------------------------------
        # 4. Multimodal Vision Search (CLIP)
        # ----------------------------------------------------
        t_clip_start = time.perf_counter()
        image_results: List[Tuple[int, float]] = []
        try:
            image_query_emb = await self.image_embedder.embed_text([cleaned_query])
            if image_query_emb.shape[0] > 0:
                image_results = await self.faiss_manager.search(
                    query_embedding=image_query_emb[0],
                    k=k * 2,
                    index_type="image",
                )
        except Exception as e:
            logger.warning(f"CLIP Image retrieval failed: {str(e)}")
        latency_tracker["clip_vision_search"] = round((time.perf_counter() - t_clip_start) * 1000, 2)

        # ----------------------------------------------------
        # 5. Adaptive Adaptive Score Filtering & Normalization
        # ----------------------------------------------------
        t_rrf_start = time.perf_counter()

        if sem_results:
            best_sem = max(score for _, score in sem_results)
            sem_results = [(cid, score) for cid, score in sem_results if score >= 0.60 * best_sem]

        if kw_results:
            best_kw = max(score for _, score in kw_results)
            kw_results = [(cid, score) for cid, score in kw_results if score >= 0.60 * best_kw]

        image_results = [(cid, s) for cid, s in image_results if s > 0.25]

        # ----------------------------------------------------
        # 6. Intent Classification & Dynamic RRF Fusion
        # ----------------------------------------------------
        query_lower = cleaned_query.lower()
        informational_patterns = ["what is", "explain", "tell me", "describe", "overview", "how to", "summary"]
        code_patterns = ["def ", "class ", "function", "error", "exception", "code", "config", "import"]
        vision_patterns = ["image", "photo", "diagram", "chart", "picture", "figure", "drawing"]

        is_informational = any(p in query_lower for p in informational_patterns)
        is_code = any(p in query_lower for p in code_patterns)
        is_vision = any(p in query_lower for p in vision_patterns)

        if is_informational:
            semantic_weight = 1.3
            keyword_weight = 0.5
            vision_weight = 0.3
        elif is_code:
            semantic_weight = 0.8
            keyword_weight = 1.2
            vision_weight = 0.2
        elif is_vision:
            semantic_weight = 0.8
            keyword_weight = 0.4
            vision_weight = 1.2
        else:
            semantic_weight = 1.0
            keyword_weight = 0.7
            vision_weight = 0.4

        results: Dict[int, HybridResult] = {}

        def update(results_list, key: str, weight: float):
            for rank, (chunk_id, score) in enumerate(results_list, start=1):
                r = results.setdefault(chunk_id, HybridResult(chunk_id=chunk_id))

                if key == "faiss":
                    r.faiss_score = float(score)
                elif key == "bm25":
                    r.bm25_score = float(score)
                elif key == "clip":
                    r.clip_score = float(score)

                r.ranks[key] = rank
                r.rrf_score += weight * (1.0 / (60.0 + rank))

        update(sem_results, "faiss", weight=semantic_weight)
        update(kw_results, "bm25", weight=keyword_weight)
        update(image_results, "clip", weight=vision_weight)

        sorted_results = sorted(
            results.values(), key=lambda x: x.rrf_score, reverse=True
        )[:k]

        latency_tracker["rrf_fusion"] = round((time.perf_counter() - t_rrf_start) * 1000, 2)

        return sorted_results
