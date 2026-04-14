from typing import List, Dict, Any
import numpy as np

from ..embeddings.text_embedder import TextEmbedder
from ..embeddings.image_embedder import ImageEmbedder
from ..chunking.document_chunker import DocumentChunker
from ..retrieval.faiss_manager import FAISSManager

class IngestionPipeline:
      """Orchestrates document ingestion: chunking + embeddings + storage."""

      def __init__(self):
            self.chunker = DocumentChunker()
            self.text_embedder = TextEmbedder()
            self.image_embedder = ImageEmbedder()
            self.faiss_manager = FAISSManager()

      async def ingest_document(self, document_id: int, text_content: str | None = None, images: List[str] | None = None, metadata: Dict[str, Any] | None = None) -> Dict[str, Any]:
            """Full ingestion pipeline for a document (text + images)"""

            all_chunks = []
            chunk_ids = []

            #1.Text Chunking & Embeddings
            if text_content:
                  text_chunks = self.chunker.chunk_text(text_content, metadata)
                  all_chunks.extend(text_content)

                  if text_chunks:
                        texts = [c["content"] for c in text_chunks]
                        text_embeddings = self.text_embedder.embed_text(texts)

                        # TODO: In real flow, chunk_ids will come from DB after save
                        # For now we simulate with indices
                        faiss_ids = await self.faiss_manager.add_embeddings(
                              text_embeddings,
                              document_id,
                              list(range(len(text_chunks)))
                        )

            if images:
                  for img_path in images:
                  # For demo we assume a simple description; in production use captioning model
                        image_desc = f"Image from document: {metadata.get('title', 'Untitled')}"
                        image_chunks = self.chunker.chunk_image_description(
                              image_desc, img_path, metadata
                        )
                        all_chunks.extend(image_chunks)

                        if image_chunks:
                              image_embeddings = await self.image_embedder.embed_image([img_path])
                              faiss_ids = await self.faiss_manager.add_embeddings(
                                    image_embeddings,
                                    document_id,
                                    list(range(len(all_chunks) - len(image_chunks), len(all_chunks)))
                              )

            return {
                  "document_id":document_id,
                  "total_chunks":len(all_chunks),
                  "status":"ingested",
                  "faiss_vector_added":self.faiss_manager.index.ntotal if self.faiss_manager.index else 0
            }

