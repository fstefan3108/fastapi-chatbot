from fastapi import HTTPException

from app.api.deps import db_dependency
from app.core.security import hash_password
from app.models.user import User
from app.schemas.user import UserRequest


def create_user(user: UserRequest, db: db_dependency):
    if db.query(User).filter(User.username == user.username).first() is None:
        new_user = User(
            username = user.username,
            email = user.email,
            hashed_password = hash_password(user.password) # Call hash_password from security.py #
        )
    else:
        raise HTTPException(status_code=409, detail="User already exists")

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


def get_users(db: db_dependency):
    users = db.query(User).all()
    return users


# Optional: Implement username/password updates later on #