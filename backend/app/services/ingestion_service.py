from typing import List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession

from ..db.repositories.base_repository import BaseRepository
from ..db.models.document import Document
from ..db.models.chunk import Chunk
from ..ml.pipelines.ingestion_pipeline import IngestionPipeline

class IngestionService:
      """Business logic for document ingestion"""

      def __init__(self):
            self.document_repo = BaseRepository(Document)
            self.chunk_repo = BaseRepository(Chunk)
            self.pipeline = IngestionPipeline()

      async def ingest(
            self, 
            db:AsyncSession,
            title:str,
            file_name:str,
            file_type:str,
            content:str | None = None,
            images: List[str] | None = None,
            user_id: int | None = None
      ) -> Dict[str, Any]:
            """Correct flow: Save Document → Save Chunks → Embed → Index."""

            # 1. Save document metadata
            document = Document(
                  title=title,
                  file_name=file_name,
                  file_type=file_type,
                  content_summary=content[:500] if content else None,
                  user_id=user_id
            )
            db.add(document)
            await db.flush()  # Get document.id

            # 2. Create and save Chunks (DB first)
            all_chunks = []
            if content:
                  chunk_dicts = self.pipeline.chunker.chunk_text(content, {"title": title})
                  for cd in chunk_dicts:
                        chunk = Chunk(
                              document_id=document.id,
                              chunk_index=cd["chunk_index"],
                              content=cd["content"],
                              chunk_type=cd["chunk_type"],
                              metadata_json=cd.get("metadata")   # Pass dict directly – JSON column handles it
                        )
                        db.add(chunk)
                        all_chunks.append(chunk)

            await db.commit()
            await db.refresh(document)

            # Convert to dict with real IDs for pipeline
            chunk_list_for_pipeline = [
                  {
                        "id": c.id,
                        "content": c.content,
                        "chunk_type": c.chunk_type,
                        "metadata": c.metadata_json or {}   # Now safely a dict
                  }
                  for c in all_chunks
            ]  

            # 3. Index in vector stores
            pipeline_result = await self.pipeline.ingest_chunks(document.id, chunk_list_for_pipeline)

            return {
                  "document_id": document.id,
                  "title": title,
                  "status": "success",
                  "chunks_created": len(all_chunks),
                  "faiss_vectors_total": pipeline_result["faiss_vectors"],
                  "vectors_added": pipeline_result["vectors_added"],
                  "message": "Document ingested and indexed successfully."
            }