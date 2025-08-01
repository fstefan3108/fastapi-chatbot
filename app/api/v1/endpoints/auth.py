from typing import Annotated
from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from starlette import status
from app.api.deps import db_dependency
from app.core.security import get_access_token
from app.schemas.token import Token
from app.schemas.user import UserRequest, UserResponse
from app.services.user.service import UserService

router = APIRouter()

### Endpoint for creating a user. Checks if the username isn't already used, ###
### creates a new user based on a User Pydantic scheme (User_Request) ###
### hashes the password with bcrypt_content.hash(), adds user to DB ###


@router.post("/register", status_code=status.HTTP_201_CREATED, response_model=UserResponse)
async def create_user(user: UserRequest, db: db_dependency):
    user_service = UserService(db=db)
    new_user = await user_service.create_user(user=user)
    return UserResponse.model_validate(new_user)


### Authenticates the user and creates the JWT access token with user info (username and user_id) for said user. ###

@router.post("/login", status_code=status.HTTP_200_OK, response_model=Token)
async def login_for_access_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db: db_dependency):
    return await get_access_token(form_data=form_data, db=db)

