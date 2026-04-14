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
            faiss_results = await self.faiss_manager.search(embedding[0], k)

            #Convert faiss_id -> chunk_id
            results = []
            for faiss_id,score in faiss_results:
                  chunk_id = self.faiss_manager.get_chunk_id(faiss_id=faiss_id)
                  if chunk_id is not None:
                        results.append((chunk_id, score))
            return results


                  