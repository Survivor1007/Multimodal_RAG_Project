from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import (create_async_engine, async_sessionmaker, AsyncSession)
from sqlalchemy import text
from .base import Base
from ..core.config import settings
import asyncio

engine = create_async_engine(
      settings.DATABASE_URL,
      echo=settings.DEBUG,
      future = True,
      pool_pre_ping = True,
)

async_session = async_sessionmaker(
      bind = engine,
      expire_on_commit=False,
      class_=AsyncSession,
)

# NOTE: Only for development. Use Alembic migrations in production.
async def init_db() -> None:
      """Initialize database (create tables)."""
      async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
      """Dependency generator for async session."""
      async with async_session() as session:
            yield session