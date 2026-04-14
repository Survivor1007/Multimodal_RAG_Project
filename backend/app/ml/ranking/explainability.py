
from datetime import datetime
from typing import Any, Dict

from backend.app.ml.ranking.reranker import CrossEncoderReranker
from backend.app.ml.ranking.rrf_ranker import RRF_Ranker
from backend.app.ml.retrieval.hybrid_retriever import HybridRetriever


class ExplainabilityModlule:
      """Provides explainable ranking with detailed factors."""

      def __init__(self):
            self.hybrid_retriever = HybridRetriever()
            self.rrf_ranker = RRF_Ranker()
            self.reranker = CrossEncoderReranker()

      async def explain_ranking(
            self, 
            query:str,
            k: int = 5,
      ) -> Dict[str, Any]:
            """Return retrieved chunks with detailed explanation of why they were ranked."""

            # Step 1: Hybrid retrieval
            hybrid_results = await self.hybrid_retriever.retrieve(query, k * 3)

            # Step 2: RRF ranking
            rrf_results = await self.rrf_ranker.rank(hybrid_results, query)

            # Step 3: Get chunk content (placeholder - in Phase 6 we will fetch from DB)
            # For now we simulate explanations
            explanations = []
            for rank, (chunk_id, final_score) in enumerate(rrf_results[:k], 1):
                  explanations.append({
                  "rank": rank,
                  "chunk_id": chunk_id,
                  "final_score": round(float(final_score), 4),
                  "factors": {
                        "semantic_score": round(0.7 * final_score, 4),
                        "keyword_score": round(0.3 * final_score, 4),
                        "rrf_contribution": round(1.0 / (60 + rank), 4),
                        "reranker_boost": round(0.4 * final_score, 4)
                  },
                  "explanation": f"Ranked #{rank} due to strong semantic match and keyword overlap with query.",
                  "retrieval_method": "hybrid_faiss_bm25"
                  })
            
            return {
                  "query": query,
                  "total_candidates": len(hybrid_results),
                  "final_results": explanations,
                  "timestamp": datetime.utcnow().isoformat()
            }