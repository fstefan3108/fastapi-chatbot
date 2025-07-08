from functools import wraps
from sqlalchemy.exc import SQLAlchemyError
from fastapi import HTTPException

def db_transactional(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        db = kwargs.get("db")

        # If not passed explicitly, try to get it from self.db (in methods)
        if not db and args:
            possible_self = args[0]
            if hasattr(possible_self, "db"):
                db = getattr(possible_self, "db")
            else:
                db = possible_self  # fallback if it's not a method

        if db is None:
            raise ValueError("Database session not provided to transactional function.")

        try:
            result = func(*args, **kwargs)
            db.commit()
            return result
        except SQLAlchemyError as e:
            db.rollback()
            raise HTTPException(status_code=500, detail="Database transaction failed.")
    return wrapper
