from fastapi import APIRouter
from .endpoints.ingest import router as ingest_router
api_router = APIRouter()

api_router.include_router(ingest_router, prefix='/ingest')