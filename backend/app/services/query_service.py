from typing import List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from ..db.repositories.base_repository import BaseRepository
from ..db.repositories.document_repository import DocumentRepository
from ..db.models.chunk import Chunk
from ..ml.retrieval.hybrid_retriever import HybridRetriever
from ..ml.ranking.rrf_ranker import RRF_Ranker
from ..ml.ranking.explainability import ExplainabilityModule

class QueryService:
      """Handles search and retrieval logic"""

      def __init__(self):
            self.document_repo = DocumentRepository()
            self.chunk_repo = BaseRepository(Chunk)
            self.hybrid_retriever = HybridRetriever()
            self.reranker = RRF_Ranker()
            self.explain_module = ExplainabilityModule()
      
      async def search(self, db: AsyncSession, query: str, k: int = 5, use_reranker: bool = True) -> List[dict]:
            """Perform hybrid search and return enriched results with reliable sources."""
            # Get ranked chunk IDs
            ranked_results = await self.hybrid_retriever.retrieve(query, k * 4)

            
            
            if not ranked_results:
                  return []
            
            print("==" * 50)
            for r in ranked_results:
                  print(r)
                  print("=" * 50)

            chunk_ids = [chunk_id for chunk_id, _ in ranked_results]
            
            # ---Fetch actual chunks + document relaiably in fresh session----------------------
            raw_sources = await self.document_repo.get_chunks_with_documents(db, chunk_ids=chunk_ids)

            #---Create  lookup + preserve original rank order + strong deduplication
            chunk_map = {s["chunk_id"]: s for s in raw_sources}
            seen_chunk_ids: set[int] = set()

            results = []

            for chunk_id, score in ranked_results:
                  if chunk_id in seen_chunk_ids:
                        continue
                  seen_chunk_ids.add(chunk_id)

                  source = chunk_map.get(chunk_id)
                  if not source :
                        continue

                  source["score"] = float(score)
                  results.append(source)


                  # # Simple deduplication by content hash
                  # content_hash = hash(chunk.content[:200])
                  # if content_hash in seen_contents:
                  #       continue
                  # seen_contents.add(content_hash)

                  # metadata = chunk.metadata_json
                  # if isinstance(metadata, str):
                  #       import json
                  #       try:
                  #             metadata = json.loads(metadata)
                  #       except:
                  #             metadata = {}
                  # elif metadata is None:
                  #       metadata = {}

                  # results.append({
                  #       "chunk_id": chunk.id,
                  #       "content": chunk.content[:800] + "..." if len(chunk.content) > 800 else chunk.content,
                  #       "score": float(score),
                  #       "chunk_type": chunk.chunk_type,
                  #       "metadata": metadata or {}
                  # })

                  if len(results) >= k:
                        break
            
            if use_reranker and results:
                  results = await self.reranker.rank(results, query=query)
            
            return results