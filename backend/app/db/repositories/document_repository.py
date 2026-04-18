from typing import  Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import  select
from sqlalchemy.orm import selectinload
from ..models.document import Document
from ..repositories.base_repository import BaseRepository

class DocumentRepository(BaseRepository[Document]):
      """Creation of document and fetching them."""
      def __init__(self):
            super().__init__(Document)

      
      async def get_or_create_by_content(
            self, 
            session:AsyncSession,
            title:str,
            content:str,
            file_name: Optional[str] = None,
            file_type: Optional[str] = None,
            source_url:Optional[str] = None,
            user_id: Optional[int] = None,
            metadata_info: Optional[str] = None
      ) -> Document:
            """Prevents duplicates using content_hash."""
            content_hash = Document.compute_content_hash(content)

            #-----------First check by content hash-----------------------------------
            result = await session.execute(select(Document).where(Document.content_hash == content_hash))
            existing_doc= result.scalar_one_or_none()

            if existing_doc:
                  #-------Update Metadata if source_url or title changed--------------------------
                  if source_url  and existing_doc.source_url != source_url:
                        existing_doc.source_url = source_url
                  if title and existing_doc.title != title:
                        existing_doc.title = title
                  await session.commit()
                  return existing_doc, True
            
            #---------Create new document if document hash not found------------------------------
            new_doc = Document.create_with_hash(
                  title = title,
                  content= content,
                  file_name=file_name,
                  file_type=file_type,
                  source_url=source_url,
                  user_id = user_id,
                  metadata_info=metadata_info
            )
            session.add(new_doc)
            await session.commit()
            await session.refresh(new_doc)
            return new_doc, False
      
      async def get_document_with_chunks(self, session: AsyncSession, doc_id: int) -> Optional[Document]:
            """Reliable fetch with chunks in one query."""
            result = await session.execute(select(Document).where(Document.id == id).options(selectinload(Document.chunks)))

            return result.scalar_one_or_none()

                                           

            
