from typing import List, Tuple
import numpy as np

from .semantic_retriever import SemanticRetriever
from .keyword_retriever import KeywordRetriever
from ..embeddings.image_embedder import ImageEmbedder
from .faiss_manager import FAISSManager

class HybridRetriever:
      def __init__(self):
            self.semantic = SemanticRetriever()
            self.keyword = KeywordRetriever()
            self.image_embedder = ImageEmbedder()
            self.faiss_manager = FAISSManager()

      async def retrieve(self, query: str, k: int = 10) -> List[Tuple[int, float]]:
            """
                  Hybrid retriever:
                   - Semantic retriever 
                   -Keyword retriever
                   -Image retriever (CLIP)
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

            print("=" * 50)
            print(f"SEMANTIC RESULTS: \n {sem_results}")
            print("=" * 50)
            print("=" * 50)
            print(f"KEYWORD RESULTS: \n {kw_results}")
            print("=" * 50)
            print("=" * 50)
            print(f"IMAGE RESULTS: \n {image_results}")
            print("=" * 50)
            #=============
            #SCORE FUSION
            #=============
            score_map: dict[int, float] = {}

            for chunk_id, score in sem_results:
                  score_map[chunk_id] = score_map.get(chunk_id, 0.0) + score * 0.7

            for chunk_id, score in kw_results:
                  score_map[chunk_id] = score_map.get(chunk_id, 0.0) + score * 0.3

            for chunk_id, score in image_results:
                  score_map[chunk_id] = score_map.get(chunk_id, 0.0) + score * 0.5


            # Sort and take top-k
            sorted_results = sorted(score_map.items(), key=lambda x: x[1], reverse=True)[:k]
            return sorted_results