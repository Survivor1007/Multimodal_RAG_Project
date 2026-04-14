from typing import List, Union
import numpy as np
from PIL import Image
import torch
import asyncio

from .base_embedder import BaseEmbedder
from ...core.config import settings

class ImageEmbedder(BaseEmbedder):
      """Image embedding using OpenAI CLIP model"""

      def __init__(self):
            from transformers import CLIPProcessor, CLIPModel

            self.model_name = settings.EMBEDDING_MODEL
            self.device = "cuda" if torch.cuda.is_available() else "cpu"

            self.model = CLIPModel.from_pretrained(self.model_name).to(self.device)
            self.processor = CLIPProcessor.from_pretrained(self.model_name)
            self._dimension = self.model.config.projection_dim
      
      async def embed_text(self, texts: List[str]) -> np.ndarray:
            """Not supported for image embedder (use TextEmbedder instead)."""
            raise NotImplementedError("ImageEmbedder does not support text embedding. Use TextEmbedder.")
      
      async def embed_image(self, images: List[Union[str, Image.Image]]) -> np.ndarray:
            """Embed image asynchronously"""
            if not images:
                  return np.array([], dtype= np.float32).reshape(0, self.dimension)
            
            #Convert file paths to PIL image if needed
            pil_images = []
            for img in images:
                  if isinstance(img, str):
                        pil_images.append(Image.open(img).convert('RGB'))
                  else:
                        pil_images.append(img.convert("RGB") if isinstance(img, Image.Image) else img)
            
            #Run heavy processing in thread pool
            loop = asyncio.get_running_loop()

            def _process_and_embed():
                  inputs = self.processor(images= pil_images, return_tensors="pt", padding=True).to(self.device)
                  with torch.no_grad():
                        image_features =  self.model.get_image_features(**inputs)
                        image_features = image_features / image_features.norm(dim= 1, keepdim= True)
                  return image_features.cpu().numpy()
      
            embeddings = await loop.run_in_executor(None, _process_and_embed)

      @property
      def dimension(self) -> int:
            return self._dimension

