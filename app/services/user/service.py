from sqlalchemy.ext.asyncio import AsyncSession
from app.core.security import hash_password
from app.crud.crud_user import crud_user
from app.models import User
from app.schemas.user import UserRequest, UserCreate
from app.utils.db_transaction import db_transactional_async
from app.utils.validation import check_username


class UserService:
    def __init__(self, db: AsyncSession):
        self.db = db

    @db_transactional_async
    async def create_user(self, user: UserRequest) -> User:
        hashed_password = await hash_password(user.password)
        await check_username(user=user, db=self.db)

        user_create = UserCreate(
            **user.model_dump(),
            hashed_password=hashed_password,
        )

        new_user = await crud_user.create(db=self.db, data=user_create.model_dump())
        await self.db.refresh(new_user)
        return new_user