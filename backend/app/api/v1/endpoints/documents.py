from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, delete

from ....core.dependencies import get_db
from ....db.models.document import Document
from ....db.models.chunk import Chunk

router = APIRouter(tags=["documents"])


@router.get("/documents/list")
async def list_documents(db: AsyncSession = Depends(get_db)):
    """Fetch all ingested documents with chunk counts and metadata."""
    try:
        # Select documents with chunk counts
        stmt = (
            select(
                Document.id,
                Document.filename,
                Document.file_type,
                Document.file_size,
                Document.created_at,
                func.count(Chunk.id).label("chunk_count")
            )
            .outerjoin(Chunk, Chunk.document_id == Document.id)
            .group_by(Document.id)
            .order_by(Document.created_at.desc())
        )
        result = await db.execute(stmt)
        rows = result.all()

        documents = []
        for r in rows:
            documents.append({
                "id": r.id,
                "filename": r.filename,
                "file_type": r.file_type,
                "file_size": r.file_size or 0,
                "chunk_count": r.chunk_count or 0,
                "created_at": r.created_at.isoformat() if r.created_at else None,
            })

        return {
            "total_documents": len(documents),
            "documents": documents
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch documents: {str(e)}")


@router.get("/documents/{doc_id}/chunks")
async def get_document_chunks(doc_id: int, db: AsyncSession = Depends(get_db)):
    """Fetch chunks for a specific document."""
    try:
        stmt = select(Chunk).where(Chunk.document_id == doc_id).order_by(Chunk.chunk_index)
        result = await db.execute(stmt)
        chunks = result.scalars().all()

        return {
            "document_id": doc_id,
            "chunk_count": len(chunks),
            "chunks": [
                {
                    "chunk_id": c.id,
                    "chunk_index": c.chunk_index,
                    "content": c.content,
                    "metadata": c.metadata_json or {},
                }
                for c in chunks
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch chunks: {str(e)}")


@router.delete("/documents/{doc_id}")
async def delete_document(doc_id: int, db: AsyncSession = Depends(get_db)):
    """Delete a document and its associated chunks from database."""
    try:
        # Delete chunks first
        await db.execute(delete(Chunk).where(Chunk.document_id == doc_id))
        # Delete document
        result = await db.execute(delete(Document).where(Document.id == doc_id))
        await db.commit()

        if result.rowcount == 0:
            raise HTTPException(status_code=404, detail="Document not found")

        return {"message": f"Document {doc_id} deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to delete document: {str(e)}")
