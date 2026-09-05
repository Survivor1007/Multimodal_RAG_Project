import os
import asyncio
from typing import List, Tuple
import math
from ...core.config import settings

class CrossEncoderReranker:
      """Cross-Encoder reranker for final relevance scoring."""

      def __init__(self):
            self.model_name = settings.RERANKER_MODEL
            self._model = None
            self._lock = asyncio.Lock()
      
      async def _load_model(self):
            async with self._lock:
                  if self._model is None:
                        from sentence_transformers import CrossEncoder
                        target_path = settings.RERANKER_MODEL_PATH
                        if target_path and os.path.exists(target_path):
                              model_to_load = target_path
                        else:
                              model_to_load = self.model_name
                              
                        self._model = CrossEncoder(model_to_load, max_length=512)
      
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
                  rerank_score = float(rerank_score)

                  # Sigmoid normalizaiton
                  norm_rerank = 1 / ( 1 + math.exp(-rerank_score))

                  # Original Score
                  norm_orig = max(0.0, min(1.0, float(orig_score)))

                  # Web boost
                  web_bonus = 0.10 if chunk_id < 0 else 0.0

                  # Final weighted score
                  final_score = (
                        0.80 * norm_rerank + 
                        0.20 * norm_orig + 
                        web_bonus
                  )

                  reranked.append(
                        (chunk_id, final_score, content)
                  )

            # Sort by final score
            return sorted(reranked, key=lambda x: x[1], reverse=True)    