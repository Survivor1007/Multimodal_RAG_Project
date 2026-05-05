from typing import List, Tuple, Dict
import numpy as np
import structlog

from .semantic_retriever import SemanticRetriever
from .keyword_retriever import KeywordRetriever
from ..embeddings.image_embedder import ImageEmbedder
from .faiss_manager import FAISSManager
from ..ranking.rrf_ranker import RRF_Ranker
from .retrieval_result import HybridResult

logger = structlog.get_logger()

class HybridRetriever:
      def __init__(self):
            self.semantic = SemanticRetriever()
            self.keyword = KeywordRetriever()
            self.image_embedder = ImageEmbedder()
            self.faiss_manager = FAISSManager()
            self.rrf_ranker = RRF_Ranker()

      async def retrieve(self, query: str, k: int = 10) -> List[HybridResult]:
            """
                  ### Hybrid retriever:
                   - Semantic retriever 
                   - Keyword retriever
                   - Image retriever (CLIP)
            """
            #===============
            #TEXT + KEYWORD 
            #===============
            sem_results = await self.semantic.retrieve(query, k * 2)
            kw_results = await self.keyword.retrieve(query, k * 2)

            #================
            #IMAGE RETRIEVAL
            #================
            image_results:List[Tuple[int, float]] = []
            try:
                  #CLIP text -> Image embedding
                  image_query_emb = await self.image_embedder.embed_text([query])

                  if image_query_emb.shape[0] > 0:
                        image_results = await self.faiss_manager.search(
                              query_embedding=image_query_emb[0],
                              k = k * 2,
                              index_type= "image",
                        )
            except Exception as e:
                  print(f"Image retrieval failed: {str(e)}")

            sem_results = [(cid, s) for cid, s in sem_results if s > 0.3]
            image_results = [(cid, s) for cid, s in image_results if s > 0.25]
            
            
            logger.debug(
                  "Results came from retrivers",
                  semantic_results = sem_results,
                  keyword_results = kw_results,
                  image_results = image_results,
            )
            
            # ==========================
            # BUILD STRUCTURED RESULTS
            # ==========================
            results : Dict[int, HybridResult] = {}

            def update(results_list, key: str, weight : float):
                  for rank, (chunk_id, score) in enumerate(results_list, start= 1):
                        r = results.setdefault(chunk_id, HybridResult(chunk_id = chunk_id))

                        # Store raw score
                        if key == "faiss":
                              r.faiss_score = score
                        elif key == "bm25":
                              r.bm25_score = score
                        elif key == "clip":
                              r.clip_score= score
                        
                        # Store rank
                        r.ranks[key] = rank

                        # Accumulate RRF
                        r.rrf_score += weight * ( 1 / (60 + rank))
            
            update(sem_results, "faiss", weight= 1.0)
            update(kw_results, "bm25", weight=0.5)
            update(image_results, "clip", weight=0.3)

            sorted_results = sorted(
                  results.values(), 
                  key=lambda x: x.rrf_score, 
                  reverse=True
            )[:k]

            return sorted_results