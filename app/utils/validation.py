from fastapi import HTTPException

from app.api.deps import db_dependency
from app.models.user import User


def check_user(user, status_code, detail):
    if not user:
        raise HTTPException(status_code=status_code, detail=detail)


def check_username(user, db: db_dependency):
    existing_user = db.query(User).filter(User.username == user.username).first()
    if existing_user is not None:
        raise HTTPException(status_code=409, detail="Username already taken.")