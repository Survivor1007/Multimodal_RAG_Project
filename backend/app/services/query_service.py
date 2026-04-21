from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from collections import defaultdict
import hashlib

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
            # Get ranked chunk IDs from hybrid retrieval
            ranked_results = await self.hybrid_retriever.retrieve(query, k * 4)

            if not ranked_results:
                  return []

            chunk_ids = [chunk_id for chunk_id, _ in ranked_results]
            
            # ---Fetch actual chunks + document + content_hash relaiably in fresh session----------------------
            raw_sources = await self.document_repo.get_chunks_with_documents_and_hashes(db, chunk_ids=chunk_ids)

            #---Create  lookup + preserve original rank order + strong deduplication------------
            chunk_map = {s["chunk_id"]: s for s in raw_sources}
            doc_chunk_count: dict[str, any] = defaultdict(int)
            MAX_CHUNK_PER_DOC = 2

            seen_chunk_content: set[str] = set()
            results = []

            for chunk_id, score in ranked_results:
                  source = chunk_map.get(chunk_id)
                  if not source :
                        continue
                  
                  doc_hash = source["document_content_hash"]
                  if doc_chunk_count[doc_hash] >= MAX_CHUNK_PER_DOC:
                        continue
                  doc_chunk_count[doc_hash] += 1
                  
                  normalized_content = " ".join(source["content"].lower().split())
                  content_hash = hashlib.sha256(normalized_content.encode('utf-8')).hexdigest()

                  if content_hash in seen_chunk_content:
                        continue
                  seen_chunk_content.add(content_hash)

                  source["score"] = float(score)
                  results.append(source)

                  if len(results) >= k:
                        break
            
            if use_reranker and results:
                  results = await self.reranker.rank(results, query=query)
            
            return results