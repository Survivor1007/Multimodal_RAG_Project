from fastapi import FastAPI
from contextlib import asynccontextmanager

from .core.config import settings
from .core.logging_config import setup_logging
from .db.session import async_session, engine, init_db
from api.v1.router import api_router


@asynccontextmanager
async def lifespan(app: FastAPI):
      #Startup
      setup_logging()
      await init_db()

      print(f"🚀 {settings.PROJECT_NAME} started in {settings.ENVIRONMENT} mode")
      yield

      #Shutdown
      await engine.dispose()
      print("👋 Application shutdown complete")

async def create_app() -> FastAPI:
      app = FastAPI(
            title=settings.PROJECT_NAME,
            version="0.1.0",
            openapi_ulr=f"{settings.API_V1_STR}/openapi.json",
            lifespan=lifespan
      )

      app.include_router(api_router, prefix = settings.API_V1_STR)

      return app

