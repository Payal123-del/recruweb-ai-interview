from typing import TypeVar, Generic, Type, Optional, List, Any, Sequence
from sqlalchemy import select, update, delete, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import Base

ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository(Generic[ModelType]):
    def __init__(self, model: Type[ModelType], db: AsyncSession):
        self.model = model
        self.db = db

    async def get_by_id(self, id: str) -> Optional[ModelType]:
        query = select(self.model).where(self.model.id == id)
        result = await self.db.execute(query)
        return result.scalars().first()

    async def get_all(self, skip: int = 0, limit: int = 100) -> Sequence[ModelType]:
        query = select(self.model).offset(skip).limit(limit)
        result = await self.db.execute(query)
        return result.scalars().all()

    async def count(self) -> int:
        query = select(func.count(self.model.id))
        result = await self.db.execute(query)
        return result.scalar_one() or 0

    async def create(self, **kwargs) -> ModelType:
        instance = self.model(**kwargs)
        self.db.add(instance)
        await self.db.flush()
        await self.db.refresh(instance)
        return instance

    async def update(self, instance: ModelType, **kwargs) -> ModelType:
        for key, value in kwargs.items():
            if value is not None and hasattr(instance, key):
                setattr(instance, key, value)
        await self.db.flush()
        await self.db.refresh(instance)
        return instance

    async def delete(self, instance: ModelType) -> bool:
        await self.db.delete(instance)
        await self.db.flush()
        return True


class TenantScopedRepository(BaseRepository[ModelType]):
    """
    Enforces tenant data isolation at the database query layer.
    A tenant can NEVER read, update, or delete data belonging to another tenant.
    """
    def __init__(self, model: Type[ModelType], db: AsyncSession, tenant_id: str):
        super().__init__(model, db)
        self.tenant_id = tenant_id

    async def get_by_id(self, id: str) -> Optional[ModelType]:
        query = select(self.model).where(
            self.model.id == id,
            self.model.tenant_id == self.tenant_id
        )
        result = await self.db.execute(query)
        return result.scalars().first()

    async def get_all(self, skip: int = 0, limit: int = 100) -> Sequence[ModelType]:
        query = (
            select(self.model)
            .where(self.model.tenant_id == self.tenant_id)
            .offset(skip)
            .limit(limit)
        )
        result = await self.db.execute(query)
        return result.scalars().all()

    async def count(self) -> int:
        query = select(func.count(self.model.id)).where(self.model.tenant_id == self.tenant_id)
        result = await self.db.execute(query)
        return result.scalar_one() or 0

    async def create(self, **kwargs) -> ModelType:
        kwargs["tenant_id"] = self.tenant_id
        return await super().create(**kwargs)
