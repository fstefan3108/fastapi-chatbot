from datetime import timedelta, datetime, timezone
from typing import Annotated
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from jose import jwt
from passlib.context import CryptContext
from sqlalchemy import select
from app.api.deps import db_dependency
from app.core.config import settings
from app.models.user import User

### Checks if user exists in the DB by username, compares password with hashed password with bcrypt_content.verify() ###

bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

async def authenticate_user(username: str, password: str, db: db_dependency):

    stmt = select(User).where(User.username == username)
    result = await db.execute(stmt)
    user = result.scalars().first()

    if not user:
        return False
    if not bcrypt_context.verify(password, user.hashed_password):
        return False
    return user

### Creates a JWT for the user, sets expiration time for the token, ###
### returns the encoded JWT using the SECRET KEY ###
### and algorithm we provided. ###

def create_access_token(username: str, user_id: int, expires_delta: timedelta):
    encode = {"sub": username, "id": user_id}
    expires = datetime.now(timezone.utc) + expires_delta
    encode.update({"exp": expires})
    return jwt.encode(encode, settings.secret_key, algorithm=settings.algorithm)


# hash password #

def hash_password(password: str):
    return bcrypt_context.hash(password)


async def get_access_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db: db_dependency):
    user = await authenticate_user(form_data.username, form_data.password, db)

    if not user:
        raise HTTPException(status_code=401, detail="Invalid Credentials")

    token = create_access_token(user.username, user.id, timedelta(minutes=settings.access_token_expire_minutes))
    return {"access_token": token, "token_type": "bearer"} # Note to self: access_token must be written exactly like that. #

