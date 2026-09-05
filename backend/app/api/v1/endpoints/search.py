import time
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from ....core.dependencies import get_db
from ....services.query_service import QueryService
from ....schemas.query import SearchRequest
from ....schemas.response import SearchResponse, RetrievedChunk, LatencyBreakdown, ScoreBreakdown, RankPositions

router = APIRouter(tags=["search"])

query_service = QueryService()

@router.post("/search", response_model=SearchResponse)
async def search_documents(
    request: SearchRequest,
    db: AsyncSession = Depends(get_db)
):
    """Hybrid semantic + keyword search with per-step latency measurement."""
    t_start = time.perf_counter()
    latency_tracker = {}

    results = await query_service.search(
        db=db,
        query=request.query,
        k=request.k,
        use_reranker=request.use_reranker,
        latency_tracker=latency_tracker,
    )

    latency_tracker["total_backend_latency"] = round((time.perf_counter() - t_start) * 1000, 2)

    formatted_chunks = []
    for r in results:
        scores_data = r.get("scores", {})
        ranks_data = r.get("ranks", {})

        formatted_chunks.append(
            RetrievedChunk(
                chunk_id=r["chunk_id"],
                content=r["content"],
                score=float(r.get("score", 0.0)),
                chunk_type=r.get("chunk_type", "text"),
                metadata=r.get("metadata", {}),
                scores=ScoreBreakdown(
                    faiss_similarity=scores_data.get("faiss_similarity"),
                    bm25_score=scores_data.get("bm25_score"),
                    clip_similarity=scores_data.get("clip_similarity"),
                    rrf_score=scores_data.get("rrf_score"),
                    rerank_score=scores_data.get("rerank_score"),
                ),
                ranks=RankPositions(
                    faiss=ranks_data.get("faiss"),
                    bm25=ranks_data.get("bm25"),
                    clip=ranks_data.get("clip"),
                ),
            )
        )

    return SearchResponse(
        query=request.query,
        results=formatted_chunks,
        total_retrieved=len(formatted_chunks),
        ranking_method="hybrid_rrf_reranker" if request.use_reranker else "hybrid_rrf",
        latency_ms=LatencyBreakdown(**latency_tracker)
    )
