from typing import Optional

from fastapi import Form, APIRouter, File, UploadFile, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from ....services.ingestion_service import IngestionService
from ....core.dependencies import get_db
from ....utils.file_handlers import extract_text_from_upload

api_router = APIRouter(tags=["upload"])
ingestion_service = IngestionService()

@api_router.post("/file")
async def upload_file(
      title:str = Form(description="Title of the file"),
      file:UploadFile = File(description="Upload file of type 'txt' "),
      user_id: int | None = Form(default=None),
      db: AsyncSession = Depends(get_db)
):
      """
            Upload a file and extract the file content.
            Extracts file name and type internally.
      """

      file_name = file.filename or "unknown"
      if "." in file_name:
            file_type = file_name.split(".")[-1]
            file_name = file_name.split(".")[-2]
      else:
            file_type = "unknown"
      
      extracted_text: str = await extract_text_from_upload(file, file_type)

      result = await ingestion_service.ingest_file(
            db= db,
            title = title,
            file_name = file_name,
            file_type = file_type,
            content = extracted_text,
            user_id = user_id,
      )

      return result 

