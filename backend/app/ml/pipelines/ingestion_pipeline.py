from typing import List, Dict, Any

from ..chunking.document_chunker import DocumentChunker
from ..embeddings.text_embedder import TextEmbedder
from ..embeddings.image_embedder import ImageEmbedder
from ..retrieval.faiss_manager import FAISSManager
from ..retrieval.bm25_manager import BM25Manager


class IngestionPipeline:
      """DB-first ingestion: chunks saved first → real IDs → embeddings → vector stores."""

      def __init__(self):
            self.chunker = DocumentChunker()
            self.text_embedder = TextEmbedder()
            self.image_embedder = ImageEmbedder()
            self.faiss_manager = FAISSManager()
            self.bm25_manager = BM25Manager()

      async def ingest_chunks(self, document_id: int, chunks: List[Dict[str, Any]]) -> None:
            """Take pre-saved chunks with real DB IDs and index them."""
            if not chunks:    
                  return

            text_contents = [c["content"] for c in chunks if c["chunk_type"] == "text"]
            text_chunk_ids = [c["id"] for c in chunks if c["chunk_type"] == "text"]

            vectors_added = 0

            if text_contents:
                  embeddings = await self.text_embedder.embed_text(text_contents)
                  await self.faiss_manager.add_embeddings(embeddings, text_chunk_ids)
                  await self.bm25_manager.add_documents(text_contents, text_chunk_ids)
                  vectors_added += len(text_contents)


            # Image handling (simplified)
            for chunk in [c for c in chunks if c["chunk_type"] == "image"]:
                  img_path = chunk.get("metadata", {}).get("image_path")
                  if img_path:
                        try:
                              emb = await self.image_embedder.embed_image([img_path])
                              if emb.shape[0] > 0:
                                    await self.faiss_manager.add_embeddings(emb, [chunk["id"]])
                                    vectors_added += 1
                        except Exception as e:
                              print(f"Warning: Failed to embed image {img_path}: {e}")
                              continue
            

            return {
                  "total_chunks": len(chunks),
                  "faiss_vectors": self.faiss_manager.total_vectors,
                  "vectors_added": vectors_added
            }