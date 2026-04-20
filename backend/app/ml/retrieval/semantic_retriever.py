from typing import List, Tuple
import numpy as np

from .faiss_manager import FAISSManager
from ..embeddings.text_embedder import TextEmbedder

class SemanticRetriever:
      def __init__(self):
            self.faiss_manager = FAISSManager()
            self.embedder = TextEmbedder()

      async def retrieve(self, query:str, k : int = 10) -> List[Tuple[int, float]]:
            """Return (chunk_id, semantic_score)"""
            embedding = await self.embedder.embed_text([query])
            # print("=" * 100)
            # print(embedding)
            # print("=" * 100)
            faiss_results = await self.faiss_manager.search(embedding[0], k)

            # print('+' * 100 + "FAISS RESULTS")
            # for r in faiss_results:
            #       print(r)
            #Convert faiss_id -> chunk_id
            results = []
            for faiss_id,score in faiss_results:
                  chunk_id = self.faiss_manager.get_chunk_id(faiss_id=faiss_id)
                  if chunk_id is not None:
                        results.append((chunk_id, score))

            # print('+' * 100)
            # for r in results:
            #       print(r)
            return results


                  