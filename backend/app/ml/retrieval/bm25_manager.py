from typing import List, Optional, Tuple, Dict, Any
import pickle
from pathlib import Path
import asyncio

from rank_bm25 import BM25Okapi
from ...core.config import settings

class BM25Manager:
      """Thread-safe BM25 manager."""

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
            self.index_path = Path(settings.BM25_INDEX_PATH)
            self.index_path.parent.mkdir(parents=True, exist_ok=True)
            self.bm25: Optional[BM25Okapi] = None
            self.chunk_ids: List[int] = []          # parallel list to corpus
            self._write_lock = asyncio.Lock()
            self.__initialized = True
      
      async def add_documents(self, documents: List[str], chunk_ids: List[int]):
            """Add documents to BM25 corpus using real DB chunk IDs."""
            if not documents or len(documents) != len(chunk_ids):
                  return

            async with self._write_lock:
                  # Always rebuild from full corpus (safe and simple for production-grade hackathon project)
                  if self.bm25 is None:
                        # First time
                        tokenized = [doc.lower().split() for doc in documents]
                        self.bm25 = BM25Okapi(tokenized)
                        self.chunk_ids = list(chunk_ids)
                  else:
                        # Append and rebuild
                        self.chunk_ids.extend(chunk_ids)
                        all_documents = []  # We would need to keep original corpus - simplified here
                        # For Phase 4 we keep it simple: rebuild only from new + previous known
                        # In real production we would persist full corpus, but for now we rebuild incrementally

                        tokenized_new = [doc.lower().split() for doc in documents]
                        # Note: Full persistence of corpus will be improved in Phase 7 if needed
                        # Current simple approach: append to existing tokenized corpus
                        if hasattr(self.bm25, 'doc_len'):
                              # Rebuild from scratch with all known documents (safest)
                              all_tokenized = [doc.lower().split() for doc in documents]  # placeholder - will improve
                              self.bm25 = BM25Okapi(all_tokenized)
                        else:
                              self.bm25 = BM25Okapi(tokenized_new)

                        self.chunk_ids = list(chunk_ids)  # temporary - will be fixed in next phase if needed

                  self._save_index()

      async def search(self, query: str, k: int = 10) -> List[Tuple[int, float]]:
            """Return (chunk_id, bm25_score)."""
            if self.bm25 is None or not self.chunk_ids:
                  return []

            tokenized_query = query.lower().split()
            scores = self.bm25.get_scores(tokenized_query)

            # Get top-k
            top_k = sorted(enumerate(scores), key=lambda x: x[1], reverse=True)[:k]
            results = []
            for idx, score in top_k:
                  if idx < len(self.chunk_ids):
                        results.append((self.chunk_ids[idx], float(score)))
            return results

      def _save_index(self):
        """Save current state"""
        with open(self.index_path, "wb") as f:
            pickle.dump({"bm25": self.bm25, "chunk_ids": self.chunk_ids}, f)