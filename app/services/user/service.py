from sqlalchemy.orm import Session
from app.core.security import hash_password
from app.crud.crud_user import crud_user
from app.schemas.user import UserRequest
from app.utils.db_transaction import db_transactional
from app.utils.validation import check_username


class UserService:
    def __init__(self, db: Session):
        self.db = db

    @db_transactional
    def create_user(self, user: UserRequest):
        hashed_password = hash_password(user.password)
        check_username(user=user, db=self.db)

        values = {
            "username": user.username,
            "email": user.email,
            "hashed_password": hashed_password,
        }

        new_user = crud_user.create(db=self.db, data=values)
        return new_user