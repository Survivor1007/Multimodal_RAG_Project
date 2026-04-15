from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from ....core.dependencies import get_db
from ....services.rag_service import RAGService
from ....schemas.query import RAGRequest
from ....schemas.response import RAGResponse

router = APIRouter(tags=["rag"])

rag_service = RAGService()

@router.post("/rag", response_model=RAGResponse)
async def rag_endpoint(
    request: RAGRequest,
    db: AsyncSession = Depends(get_db)
):
      """Full RAG pipeline with retrieval + generation."""
      response = await rag_service.generate_rag_response(
            db=db,
            query=request.query,
            k=request.k
      )
      return RAGResponse(**response)