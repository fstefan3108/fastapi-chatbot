from app.crud.base import CRUDBase
from app.models.user import User

crud_user = CRUDBase[User](User)