from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Annotated
from app.core.config import settings
from app.db.async_session import AsyncSessionLocal
from app.models.user import User


# Async Session #

async def get_async_db():
    async with AsyncSessionLocal() as db:
        yield db

db_dependency = Annotated[AsyncSession, Depends(get_async_db)]


### Gets the current logged user by decoding the JWT token; ###
### Extracts user's username and ID from the JWT package, using provided key and algorithm. ###

oauth2_bearer = OAuth2PasswordBearer(tokenUrl="/v1/auth/token")

async def get_current_user(token: Annotated[str, Depends(oauth2_bearer)], db: db_dependency):
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=settings.algorithm)
        username: str = payload.get("sub")
        user_id: int = payload.get("id")

        if username is None or user_id is None:
            raise HTTPException(status_code=401, detail="Invalid Credentials")


        stmt = select(User).where(User.id == user_id)
        result = await db.execute(stmt)
        user = result.scalars().first()

        if user is None:
            raise HTTPException(status_code=404, detail="User not found")


        return {"username": username, "id": user_id}
    except JWTError:
            raise HTTPException(status_code=401, detail="Invalid Credentials")

# User dependency instantiation #
user_dependency = Annotated[dict, Depends(get_current_user)]


