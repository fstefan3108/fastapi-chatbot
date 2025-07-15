from functools import wraps
from sqlalchemy.exc import SQLAlchemyError
from fastapi import HTTPException
from app.core.logger import logger


def db_transactional_async(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        db = kwargs.get("db")

        if not db and args:
            possible_self = args[0]
            if hasattr(possible_self, "db"):
                db = getattr(possible_self, "db")
            else:
                db = possible_self

        if db is None:
            raise ValueError("Database session not provided to transactional function.")

        try:
            result = await func(*args, **kwargs)
            await db.commit()
            return result
        except SQLAlchemyError:
            await db.rollback()
            logger.exception("Exception while executing transaction.")
            raise HTTPException(status_code=500, detail="Database transaction failed.")
    return wrapper



