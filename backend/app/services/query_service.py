from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from ..db.models.chunk import Chunk

from backend.app.db.repositories.base_repository import BaseRepository
from backend.app.ml.retrieval.hybrid_retriever import HybridRetriever
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
            ranked_results = await self.hybrid_retriever.retrieve(query, k * 2)

            # Fetch actual chunk content from DB
            chunk_ids = [chunk_id for chunk_id, _ in ranked_results]
            chunks = await self.chunk_repo.get_multi(db, skip=0, limit=100)  # TODO: improve with IN query later

            chunk_map = {c.id: c for c in chunks if c.id in chunk_ids}

            results = []
            for chunk_id, score in ranked_results[:k]:
                  chunk = chunk_map.get(chunk_id)
                  if chunk:
                        results.append({
                              "chunk_id": chunk.id,
                              "content": chunk.content,
                              "score": float(score),
                              "chunk_type": chunk.chunk_type,
                              "metadata": chunk.metadata_json or {}
                        })
            
            return results