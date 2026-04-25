from typing import List, Dict, Any
import traceback

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
                  img_path = chunk.get("metadata", {}).get("path")
                  if img_path:
                        try:
                              emb = await self.image_embedder.embed_image([img_path])
                              if emb.shape[0] > 0:
                                    await self.faiss_manager.add_embeddings(emb, [chunk["id"]])
                                    vectors_added += 1
                        except Exception as e:
                              print(f"Warning: Failed to embed image {img_path}: {str(e)}")
                              traceback.print_exc()
                              continue
            

            return {
                  "total_chunks": len(chunks),
                  "faiss_vectors": self.faiss_manager.total_vectors,
                  "vectors_added": vectors_added
            }
      #=========================
      #TEXT ONLY INGESTION (v2)
      #=========================
      async def ingest_text_chunks(
            self, 
            document_id:int,
            chunks:List[Dict[str, Any]],
      ) -> Dict[str, Any]:
            """
                  Clean text only ingestion.
                  No image handling.
            """

            if not chunks:
                  return {
                        "total_chunks": 0,
                        "faiss_vectors": self.faiss_manager.total_vectors,
                        "vectors_added": 0,
                  }
            
            text_chunks = [c for c in chunks if c["chunk_type"] == "text"]
            if not text_chunks:
                  return {
                        "total_chunks": 0,
                        "faiss_vectors": self.faiss_manager.total_vectors,
                        "vectors_added": 0,
                  }
            
            text_content = [c["content"] for c in text_chunks]
            text_ids = [c["id"] for c  in text_chunks]

            vectors_added = 0

            try:
                  #Generate embeddings
                  embeddings = await self.text_embedder.embed_text(text_content)
                  #Store in FAISS
                  await self.faiss_manager.add_embeddings(embeddings=embeddings, chunk_ids=text_ids, index_type="text")
                  #Store in BM25
                  await self.bm25_manager.add_documents(text_content,text_ids)

                  vectors_added = len(text_content)
            except Exception as e :
                  print(f"Text embeddings failed: {str(e)}")
                  traceback.print_exc()
            
            return {
                  "total_chunks": len(text_chunks),
                  "faiss_vectors": self.faiss_manager.get_total_vectors("text"),
                  "vectors_added": vectors_added,
            }
      #==================================
      #PIPELINE FOR IMAGE INGESTION (v2)
      #==================================
      async def ingest_image_chunks(
            self, 
            document_id:int,
            chunks: List[Dict[str, Any]],
      ) -> Dict[str, Any]:
            """
                  Clean image-only ingestion for v2
            """
            if not chunks:
                  return {
                        "total_chunks": 0,
                        "faiss_vectors": self.faiss_manager.get_total_vectors("image"),
                        "vectors_added": 0,
                  }
            image_chunks = [c for c in chunks if c["chunk_type"] == "image"]            
            if not image_chunks:
                  return {
                        "total_chunks": 0,
                        "faiss_vectors": self.faiss_manager.get_total_vectors("image"),
                        "vectors_added": 0,
                  }
            
            vectors_added = 0
            for chunk in image_chunks:
                  img_path = chunk.get("metadata", {}).get("path")
                  if not img_path:
                        continue

                  try:
                        #Generate embedding
                        emb = await self.image_embedder.embed_image([img_path])
                        if emb.shape[0] == 0:
                              continue
                        #Store in FAISS (image index)
                        await self.faiss_manager.add_embeddings(
                              embeddings=emb,
                              chunk_ids=[chunk["id"]],
                              index_type="image",
                        )
                        vectors_added += 1
                  except Exception as e:
                        print(f"Failed image embedding: {str(e)}")
                        traceback.print_exc()
                        continue
            
            return {
                  "total_chunks": len(image_chunks),
                  "faiss_vectors": self.faiss_manager.get_total_vectors("image"),
                  "vectors_added": vectors_added,
            }
