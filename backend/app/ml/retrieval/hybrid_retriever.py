from typing import List, Tuple
import numpy as np
import logging
from .semantic_retriever import SemanticRetriever
from .keyword_retriever import KeywordRetriever
from ..embeddings.image_embedder import ImageEmbedder
from .faiss_manager import FAISSManager
from ..ranking.rrf_ranker import RRF_Ranker

logger = logging.getLogger(__name__)

class HybridRetriever:
      def __init__(self):
            self.semantic = SemanticRetriever()
            self.keyword = KeywordRetriever()
            self.image_embedder = ImageEmbedder()
            self.faiss_manager = FAISSManager()
            self.rrf_ranker = RRF_Ranker()

      async def retrieve(self, query: str, k: int = 10) -> List[Tuple[int, float]]:
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
            
            
            logger.debug("SEM:", sem_results[:5])
            logger.debug("KW:", kw_results[:5])
            logger.debug("IMG:", image_results[:5])
            
            #=============
            #SCORE FUSION
            #=============
            score_map: dict[int, float] = {}
            
            def rrf_fusion(weighted_lists, k=60):
                  score_map: dict[int, float] = {}

                  for results, weight in weighted_lists:
                        for rank, (chunk_id, _) in enumerate(results, start=1):
                              score = weight * (1 / (k + rank))
                              score_map[chunk_id] = score_map.get(chunk_id, 0.0) + score

                  return score_map
            
            score_map = rrf_fusion([
                  (sem_results, 1.0),
                  (kw_results, 0.5),
                  (image_results, 0.3),
            ])
            sorted_results = sorted(score_map.items(), key=lambda x: x[1], reverse=True)[:k]
            return sorted_results