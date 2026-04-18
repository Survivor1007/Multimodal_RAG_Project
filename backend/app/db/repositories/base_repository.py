from typing import Type, TypeVar, Generic, Optional, List, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select 
from sqlalchemy import delete
from ..base import Base

ModelType = TypeVar("ModelType", bound= Base)

class BaseRepository(Generic[ModelType]):
      """Base repository with basic CRUD operations"""

      def __init__(self, model: Type[ModelType]):
            self.model = model
      
      # async def get(self, db: AsyncSession, id: Any) -> ModelType | None:
      #       result  = await db.execute(select(self.model).where(self.model.id == id))
      #       return result.scalar_one_or_none()
      # async def get_multi(self, db: AsyncSession, *, skip: int = 0, limit: int  = 100) -> list[ModelType]:
      #       result  = await db.execute(select(self.model).offset(skip).limit(limit))
      #       return list(result.scalars().all())

      #-------FUNCTIONS TO FETCH ONE/MANY FILES---------------------------------------------
      async def get_by_id(self, db:AsyncSession, id: Any) -> ModelType | None:
            result = await db.execute(select(self.model).where(self.model.id == id))
            return result.scalar_one_or_none()

      async def get_all(self, session: AsyncSession, skip:int = 0, limit: int = 50) -> List[ModelType]:
            result = await session.execute(select(self.model).offset(skip).limit(limit))
            return result.scalars().all()
      
      #-------USED TO DELETE A TUPLE IN THE DATABASE--------------------------------------------
      async def delete(self, session: AsyncSession, id: int) -> bool:
            result = await session.execute(delete(self.model).where(self.model.id == id))
            await session.commit()
            return result.rowcount > 0
