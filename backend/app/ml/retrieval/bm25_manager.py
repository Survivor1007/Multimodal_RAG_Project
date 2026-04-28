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
            self.corpus: List[str] = []
            self.load_index()
      
      async def add_documents(self, documents: List[str], chunk_ids: List[int]):
            """Add documents to BM25 corpus using real DB chunk IDs."""
            if not documents or len(documents) != len(chunk_ids):
                  return

            async with self._write_lock:
                  # if self.bm25 is None:
                  #       # First time
                  #       tokenized = [doc.lower().split() for doc in documents]
                  #       self.bm25 = BM25Okapi(tokenized)
                  #       self.chunk_ids = list(chunk_ids)
                  # else:
                  #       # Append and rebuild
                  #       self.chunk_ids.extend(chunk_ids)
                  #       all_documents = [] 

                  #       tokenized_new = [doc.lower().split() for doc in documents]
                  #       if hasattr(self.bm25, 'doc_len'):
                  #             all_tokenized = [doc.lower().split() for doc in documents] 
                  #             self.bm25 = BM25Okapi(all_tokenized)
                  #       else:
                  #             self.bm25 = BM25Okapi(tokenized_new)

                  #       self.chunk_ids = list(chunk_ids)  # temporary - will be fixed in next phase if needed
                  self.corpus.extend(documents)
                  self.chunk_ids.extend(chunk_ids)

                  # Rebuild BM25 from full corpus
                  tokenized = [doc.lower().split() for doc in self.corpus]
                  self.bm25 = BM25Okapi(tokenized)

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
            pickle.dump({"bm25": self.bm25, "chunk_ids": self.chunk_ids, "corpus" : self.corpus}, f)
      
      def load_index(self):
            if not self.index_path.exists():
                  return

            with open(self.index_path, "rb") as f:
                  data = pickle.load(f)
                  self.bm25 = data.get("bm25")
                  self.chunk_ids = data.get("chunk_ids", [])
                  self.corpus = data.get("corpus", [])