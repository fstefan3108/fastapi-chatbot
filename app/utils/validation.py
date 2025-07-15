from fastapi import HTTPException
from sqlalchemy import select
from app.api.deps import db_dependency
from app.models.user import User

async def check_username(user, db: db_dependency):
    stmt = select(User).where(User.username == user.username)
    result = await db.execute(stmt)
    existing_user = result.scalars().first()
    if existing_user is not None:
        raise HTTPException(status_code=409, detail="Username already taken.")