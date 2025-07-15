from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session


### Self note: Key differences between previous sync version and new async version: ###
### In the sync version, data from the tables is already available for use/querying/filtering ###
### In the async version, we first wait for the select query to execute asynchronously, await the results ###
### And unpack the results with .scalars() for later use. (stmt = statement) ###


class CRUDBase:
    def __init__(self, model):
        self.model = model

    async def create(self, db: AsyncSession, data: dict):
        item = self.model(**data)
        db.add(item)
        await db.flush()
        await db.refresh(item)
        return item

    def create_sync(self, db: Session, data: dict):
        item = self.model(**data)
        db.add(item)
        db.flush()
        db.refresh(item)
        return item

    async def get_by(self, db: AsyncSession, criteria=None, order=None):

        stmt = select(self.model)
        if criteria is not None:
            stmt = stmt.where(criteria)
        if order is not None:
            stmt = stmt.order_by(order)

        result = await db.execute(stmt)
        return result.scalars().all()

    def get_by_sync(self, db: Session, criteria=None, order=None):

        query = db.query(self.model)
        if criteria is not None:
            query = query.filter(criteria)
        if order is not None:
            query = query.order_by(order)
        return query.all()

    async def get_first(self, db: AsyncSession, criteria=None):

        stmt = select(self.model)
        if criteria is not None:
            stmt = stmt.where(criteria)

        result = await db.execute(stmt)
        return result.scalars().first()
