from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from ....core.dependencies import get_db
from ....services.query_service import QueryService
from ....schemas.query import SearchRequest
from ....schemas.response import SearchResponse

router = APIRouter(tags=["search"])

query_service = QueryService()

@router.post("/search", response_model=SearchResponse)
async def search_documents(
    request: SearchRequest,
    db: AsyncSession = Depends(get_db)
):
      """Hybrid semantic + keyword search with ranking."""
      results = await query_service.search(
            db=db,
            query=request.query,
            k=request.k,
            use_reranker=request.use_reranker
      )

      return SearchResponse(
            query=request.query,
            results=results,
            total_retrieved=len(results),
            ranking_method="hybrid_rrf_reranker"
      )
