import os
import faiss
import numpy as np
from typing import List, Tuple, Optional, Dict
import pickle
from pathlib import Path
import asyncio

from ...core.config import settings


class FAISSManager:
      """Singleton + thread-safe FAISS manager (shared across ingestion & search)."""

      _instance = None
      _lock = asyncio.Lock()

      def __new__(cls):
            if cls._instance is None:
                  cls._instance = super().__new__(cls)
                  cls._instance.__initialized = False
            return cls._instance

      def __init__(self):
            if self.__initialized:
                  return 
            self.index_path = Path(settings.FAISS_INDEX_PATH)
            self.index_path.parent.mkdir(parents=True, exist_ok=True)
            self.dimension: Optional[int] = None
            self.index: Optional[faiss.IndexFlatIP] = None
            self.faiss_to_chunk: Dict[int, int] = {}   # faiss_id → real DB chunk_id
            self._write_lock = asyncio.Lock()
            self.__initialized = True

      async def _initialize_index(self, dimension: int):
            """Ensure index is initialized."""
            async with self._write_lock:
                  if self.index is not None:
                        return
                  if self.index_path.exists():
                        self.index = faiss.read_index(str(self.index_path))
                        self.dimension = self.index.d
                        mapping_path = self.index_path.with_suffix(".mapping.pkl")
                        if mapping_path.exists():
                              with open(mapping_path, "rb") as f:
                                    self.faiss_to_chunk = pickle.load(f)
                  else:
                        self.dimension = dimension
                        self.index = faiss.IndexFlatIP(dimension)

      async def add_embeddings(self, embeddings: np.ndarray, chunk_ids: List[int]) -> List[int]:
            """Add embeddings using real DB chunk IDs."""
            if len(embeddings) == 0 or len(embeddings) != len(chunk_ids):
                  return []

            await self._initialize_index(embeddings.shape[1])

            async with self._write_lock:
                  faiss.normalize_L2(embeddings)
                  start_id = self.index.ntotal if self.index is not None else 0
                  self.index.add(embeddings)

                  faiss_ids = list(range(start_id, start_id + len(chunk_ids)))
                  for f_id, c_id in zip(faiss_ids, chunk_ids):
                        self.faiss_to_chunk[f_id] = c_id

                  self._save_index()
                  return faiss_ids

      async def search(self, query_embedding: np.ndarray, k: int = 10) -> List[Tuple[int, float]]:
            """Search – thread-safe for reads."""

            await self._initialize_index(query_embedding.shape[0])


            if self.index is None or self.index.ntotal == 0:
                  return []

            

            query_embedding = query_embedding.reshape(1, -1).astype(np.float32)
            faiss.normalize_L2(query_embedding)

            scores, indices = self.index.search(query_embedding, k)
            results = []
            # print("==" * 50)
            # print("FAISS total vectors:", self.total_vectors)
            # print("==" * 50)

            for idx, score in zip(indices[0], scores[0]):
                  if idx != -1:
                        results.append((int(idx), float(score)))
            return results

      def _save_index(self):
            """Persist index and mapping."""
            if self.index is None:
                  return
            faiss.write_index(self.index, str(self.index_path))
            mapping_path = self.index_path.with_suffix(".mapping.pkl")
            with open(mapping_path, "wb") as f:
                  pickle.dump(self.faiss_to_chunk, f)

      def get_chunk_id(self, faiss_id: int) -> Optional[int]:
            return self.faiss_to_chunk.get(faiss_id)

      @property
      def total_vectors(self) -> int:
            """Safe access to ntotal."""
            if self.index is None:
                  return 0
            return self.index.ntotal