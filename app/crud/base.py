from typing import Optional, Generic, TypeVar, Type
from sqlalchemy import select, delete, update
from sqlalchemy.ext.asyncio import AsyncSession

ModelType = TypeVar("ModelType")

### Self note: Key differences between previous sync version and new async version: ###
### In the sync version, data from the tables is already available for use/querying/filtering ###
### In the async version, we first wait for the select query to execute asynchronously, await the results ###
### And unpack the results with .scalars() for later use. (stmt = statement) ###


class CRUDBase(Generic[ModelType]):
    def __init__(self, model: Type[ModelType]):
        self.model = model

    async def create(self, db: AsyncSession, data: dict) -> ModelType:
        item = self.model(**data)
        db.add(item)
        await db.flush()
        await db.refresh(item)
        return item

    async def get_all(self, db: AsyncSession, limit: Optional[int] = None, criteria: Optional = None, order: Optional = None) -> list[ModelType]:
        stmt = select(self.model)
        if criteria is not None:
            stmt = stmt.where(criteria)
        if order is not None:
            stmt = stmt.order_by(order)
        if limit is not None:
            stmt = stmt.limit(limit)

        result = await db.execute(stmt)
        return list(result.scalars().all())

    async def get_single(self, db: AsyncSession, criteria: Optional = None) -> Optional[ModelType]:
        stmt = select(self.model)
        if criteria is not None:
            stmt = stmt.where(criteria)

        result = await db.execute(stmt)
        return result.scalars().first()

    async def delete(self, db: AsyncSession, criteria: Optional = None) -> None:
        stmt = delete(self.model)
        if criteria is not None:
            stmt = stmt.where(criteria)

        await db.execute(stmt)

    async def update(self, db: AsyncSession, values: dict, criteria: Optional = None) -> Optional[ModelType]:
        stmt = update(self.model).values(**values)
        if criteria is not None:
            stmt = stmt.where(criteria)

        result = await db.execute(stmt)
        return result.scalars().first()


