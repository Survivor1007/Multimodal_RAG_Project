from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession

from ....core.dependencies import get_db
from ....services.ingestion_service import IngestionService
from ....schemas.ingest import IngestRequest, IngestResponse  # will be created in Phase 6, using placeholder for now

router = APIRouter(tags=["ingest"])

ingestion_service = IngestionService()

@router.post('/ingest', response_model=dict)
async def ingest_document(
    title: str = Form(...),
    file_name: str = Form(...),
    file_type: str = Form(...),
    content: str = Form(None),
    files: List[UploadFile] = File(None),  # images or documents
    user_id: int | None = Form(None),
    db: AsyncSession = Depends(get_db),
):
      """Ingest a document with text and/or images."""
      try:
            # For simplicity in Phase 3: support text + image paths (in production handle file upload properly)
            image_paths = []
            if files:
                  for file in files:
                  # In real implementation: save file and pass path
                        image_paths.append(f"temp/{file.filename}")  # placeholder

            result = await ingestion_service.ingest(
                  db=db,
                  title=title,
                  file_name=file_name,
                  file_type=file_type,
                  content=content,
                  images=image_paths or None,
                  user_id=user_id,
            )
            return result
      except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))