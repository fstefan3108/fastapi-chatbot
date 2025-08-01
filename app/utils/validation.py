from fastapi import HTTPException
from app.api.deps import db_dependency
from app.crud.crud_user import crud_user
from app.crud.crud_website import crud_website
from app.models import Website
from app.models.user import User

async def check_username(user, db: db_dependency):
    existing_user = await crud_user.get_single(db=db, criteria=User.username == user.username)
    if existing_user is not None:
        raise HTTPException(status_code=409, detail="Username already taken.")

async def check_website(url: str, db: db_dependency):
    existing_website = await crud_website.get_single(db=db, criteria=Website.url == url)
    if existing_website is not None:
        raise HTTPException(status_code=409, detail="Website already exists.")