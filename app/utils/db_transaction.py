from functools import wraps
from sqlalchemy.exc import SQLAlchemyError
from fastapi import HTTPException

def db_transactional(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        db = kwargs.get("db") or (args[0] if args else None)

        if db is None:
            raise ValueError("Database session not provided to transactional function.")

        try:
            with db.begin():
                return func(*args, **kwargs)
        except SQLAlchemyError as e:
            raise HTTPException(status_code=500, detail="Database transaction failed.")
    return wrapper