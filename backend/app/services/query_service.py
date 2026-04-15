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
            ranked_results = await self.hybrid_retriever.retrieve(query, k * 4)

            if not ranked_results:
                  return []

            chunk_ids = [chunk_id for chunk_id, _ in ranked_results]
            
            # Fetch actual chunk content from DB
            stmt = select(Chunk).where(Chunk.id.in_(chunk_ids))
            result = await db.execute(stmt)
            chunks = result.scalars().all()

            # Create lookup map
            chunk_map = {chunk.id: chunk for chunk in chunks}

            # Build results while preserving rank order and avoiding duplicates
            seen_contents = set()
            results = []

            for chunk_id, score in ranked_results:
                  chunk = chunk_map.get(chunk_id)
                  if not chunk:
                        continue

                  # Simple deduplication by content hash
                  content_hash = hash(chunk.content[:200])
                  if content_hash in seen_contents:
                        continue
                  seen_contents.add(content_hash)

                  metadata = chunk.metadata_json
                  if isinstance(metadata, str):
                        import json
                        try:
                              metadata = json.loads(metadata)
                        except:
                              metadata = {}
                  elif metadata is None:
                        metadata = {}

                  results.append({
                        "chunk_id": chunk.id,
                        "content": chunk.content[:800] + "..." if len(chunk.content) > 800 else chunk.content,
                        "score": float(score),
                        "chunk_type": chunk.chunk_type,
                        "metadata": metadata or {}
                  })

                  if len(results) >= k:
                        break
            
            return results