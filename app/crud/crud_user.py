from app.api.deps import db_dependency
from app.core.security import hash_password
from app.crud.base import create, get_by
from app.models.user import User
from app.schemas.user import UserRequest
from app.utils.db_transaction import db_transactional
from app.utils.validation import check_username


@db_transactional
def create_user(user: UserRequest, db: db_dependency):
    hashed_password = hash_password(user.password)
    check_username(user=user, db=db)

    values = {
        "username": user.username,
        "email": user.email,
        "hashed_password": hashed_password,
    }

    new_user = create(model=User, db=db, data=values)
    return new_user


def get_users(db: db_dependency):
    users = get_by(model=User, db=db)
    return users



# Optional: Implement username/password updates later on #