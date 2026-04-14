from typing import List
import numpy as np
from sentence_transformers import SentenceTransformer
import torch 
import asyncio

from .base_embedder import BaseEmbeder
from ...core.config import settings

class TextEmbedder(BaseEmbeder):
      """Text embedder using sentence transformers"""

      def __init__(self):
            self.model_name = settings.EMBEDDING_MODEL
            self.device = "cuda" if torch.cuda.is_available() else "cpu"
            self.model = SentenceTransformer(self.model_name, device = self.device)
            self._dimension = self.model.get_sentence_embedding_dimension()

      async def embed_text(self, texts: List[str]) -> np.ndarray:
            """Embed text asynchronously"""
            if not texts:
                  return np.array([], dtype=np.flaot32).reshape(0, self.dimension)
      

            #Run CPU/GPU heavy interferenc in thread pool
            loop = asyncio.get_running_loop()
            embeddings = await loop.run_in_executor(
                  None, self.model.encode, texts, convert_to_numpy = True, normalize_embeddings = True
            )

            return embeddings
      
      async def embed_image(self, images: List) -> np.ndarray:
            """Not supported for text embedder."""
            raise NotImplementedError("TextEmbedder does not support image embedding. Use ImageEmbedder.")

      @property
      def dimension(self) -> int:
            return self._dimension