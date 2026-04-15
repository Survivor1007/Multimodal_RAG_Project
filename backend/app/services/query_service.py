from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from ..db.repositories.base_repository import BaseRepository
from ..db.models.chunk import Chunk
from ..ml.retrieval.hybrid_retriever import HybridRetriever
from ..ml.ranking.explainability import ExplainabilityModule

class QueryService:
      """Handles search and retrieval logic"""

      def __init__(self):
            self.chunk_repo = BaseRepository(Chunk)
            self.hybrid_retriever = HybridRetriever()
            self.explain_module = ExplainabilityModule()
      
      async def search(self, db: AsyncSession, query: str, k: int = 5, use_reranker: bool = True) -> List[dict]:
            """Perform hybrid search and return enriched results."""
            # Get ranked chunk IDs
            ranked_results = await self.hybrid_retriever.retrieve(query, k * 3)

            if not ranked_results:
                  return []

            chunk_ids = [chunk_id for chunk_id, _ in ranked_results]
            
            # Fetch actual chunk content from DB
            stmt = select(Chunk).where(Chunk.id.in_(chunk_ids))
            result = await db.execute(stmt)
            chunks = result.scalars().all()

            # Create lookup map
            chunk_map = {chunk.id: chunk for chunk in chunks}

            # Step 3: Build enriched results in ranked order
            results = []
            for chunk_id, score in ranked_results[:k]:
                  chunk = chunk_map.get(chunk_id)
                  if chunk:
                        results.append({
                              "chunk_id": chunk.id,
                              "content": chunk.content[:800] + "..." if len(chunk.content) > 800 else chunk.content,
                              "score": float(score),
                              "chunk_type": chunk.chunk_type,
                              "metadata": chunk.metadata_json or {}
                        })
            
            return results