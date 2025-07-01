from typing import Annotated
from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from starlette import status
from app.api.deps import db_dependency
from app.core.security import get_access_token
from app.crud.crud_user import create_user, get_users
from app.schemas.token import Token
from app.schemas.user import UserRequest
from app.utils.validation import check_user

router = APIRouter()



### Endpoint for creating a user. Checks if the username isnt already used, ###
### creates a new user based on a User Pydantic scheme (User_Request) ###
### hashes the password with bcrypt_content.hash(), adds user to DB ###

@router.post("/create_user", status_code=status.HTTP_201_CREATED)
async def create_user_endpoint(user: UserRequest, db: db_dependency):
    new_user = create_user(db=db, user=user)
    return new_user




### Gets all users from the DB. ###

@router.get("/users/", status_code=status.HTTP_200_OK)
async def get_users_endpoint(db: db_dependency):
    users = get_users(db=db)
    check_user(user=users, status_code=404, detail="Users not found.")
    return users


### Authenticates the user and creates the JWT access token with user info (username and user_id) for said user. ###

@router.post("/token", response_model=Token)
async def login_for_access_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db: db_dependency):
    return get_access_token(form_data=form_data, db=db)

