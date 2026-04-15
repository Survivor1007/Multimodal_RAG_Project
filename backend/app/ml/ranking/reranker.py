import asyncio
from typing import List, Tuple


class CrossEncoderReranker:
      """Cross-Encoder reranker for final relevance scoring."""

      def __init__(self):
            self.model_name = "cross-encoder/ms-marco-MiniLM-L-6-v2"
            self._model = None
            self._lock = asyncio.Lock()
      
      async def _load_model(self):
            async with self._lock:
                  if self._model is None:
                        from sentence_transformers import CrossEncoder
                        self._model = CrossEncoder(self.model_name, max_length=512)
      
      async def rerank(self, query: str, candidates: List[Tuple[int, float, str]]) -> List[Tuple[int, float,str]]:
            """Rerank candidates using cross-encoder. candidates = [(chunk_id, score, content)]"""
            if not candidates:
                  return []

            await self._load_model()

            # Prepare pairs
            pairs = [(query, content) for _, _, content in candidates]

            loop = asyncio.get_running_loop()
            rerank_scores = await loop.run_in_executor(
                  None, self._model.predict, pairs
            )

            # Combine original score + reranker score
            reranked = []
            for (chunk_id, orig_score, content), rerank_score in zip(candidates, rerank_scores):
                  # Normalize original score and avoid negative impact
                  norm_orig = max(0.0, float(orig_score))
                  final_score = 0.65 * norm_orig + 0.35 * float(rerank_score)
                  reranked.append((chunk_id, final_score, content))

            # Sort by final score
            return sorted(reranked, key=lambda x: x[1], reverse=True)