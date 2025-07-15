from sqlalchemy.ext.asyncio import AsyncSession
from app.core.security import hash_password
from app.crud.crud_user import crud_user
from app.schemas.user import UserRequest
from app.utils.validation import check_username


class UserService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_user(self, user: UserRequest):
        hashed_password = hash_password(user.password)
        await check_username(user=user, db=self.db)

        values = {
            "username": user.username,
            "email": user.email,
            "hashed_password": hashed_password,
        }

        new_user = await crud_user.create(db=self.db, data=values)
        return new_user