from typing import Type, TypeVar, Generic, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select 
from ..base import Base

ModelType = TypeVar("ModelType", bound= Base)

class BaseRepository(Generic[ModelType]):
      """Base repository with basic CRUD operations"""

      def __init__(self, model: Type[ModelType]):
            self.model = model
      
      async def get(self, db: AsyncSession, id: Any) -> ModelType | None:
            result  = await db.execute(select(self.model).where(self.model.id == id))
            return result.scalar_one_or_none()
      async def get_multi(self, db: AsyncSession, *, skip: int = 0, limit: int  = 100) -> list[ModelType]:
            result  = await db.execute(select(self.model).offset(skip).limit(limit))
            return list(result.scalars().all())