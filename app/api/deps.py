from fastapi import Depends, HTTPException, Security
from fastapi.security import OAuth2PasswordBearer, APIKeyHeader
from jose import jwt, JWTError
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Annotated
from app.core.config import settings
from app.crud.crud_user import crud_user
from app.crud.crud_website import crud_website
from app.db.async_session import AsyncSessionLocal
from app.models import Website
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

        user = await crud_user.get_single(db=db, criteria=User.id==user_id)

        if user is None:
            raise HTTPException(status_code=404, detail="User not found")

        return user
    except JWTError:
            raise HTTPException(status_code=401, detail="Invalid Credentials")

# User dependency instantiation #
user_dependency = Annotated[User, Depends(get_current_user)]

# API Key dependency #

header_scheme = APIKeyHeader(name="x-key", auto_error=False)

async def get_current_website(db: db_dependency, api_key: str = Security(header_scheme)):
    if not api_key:
        raise HTTPException(status_code=403, detail="Missing API Key")
    website = await crud_website.get_single(db=db, criteria=Website.api_key==api_key)
    if not website:
        raise HTTPException(status_code=403, detail="Invalid API Key")
    return website

api_key_dependency = Annotated[Website, Depends(get_current_website)]


