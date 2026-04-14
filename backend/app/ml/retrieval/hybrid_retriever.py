from typing import List, Tuple
import numpy as np

from .semantic_retriever import SemanticRetriever
from .keyword_retriever import KeywordRetriever

class HybridRetriever:
      def __init__(self):
            self.semantic = SemanticRetriever()
            self.keyword = KeywordRetriever()

      async def retrieve(self, query: str, k: int = 10) -> List[Tuple[int, float]]:
            """Hybrid retrieval with simple score fusion (can be upgraded to RRF later)."""
            sem_results = await self.semantic.retrieve(query, k * 2)
            kw_results = await self.keyword.retrieve(query, k * 2)

            # Combine and normalize scores
            score_map: dict[int, float] = {}
            for chunk_id, score in sem_results:
                  score_map[chunk_id] = score_map.get(chunk_id, 0.0) + score * 0.7
            for chunk_id, score in kw_results:
                  score_map[chunk_id] = score_map.get(chunk_id, 0.0) + score * 0.3

            # Sort and take top-k
            sorted_results = sorted(score_map.items(), key=lambda x: x[1], reverse=True)[:k]
            return sorted_results