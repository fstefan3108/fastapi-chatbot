from app.crud.base import CRUDBase
from app.models.user import User

class CRUDUser(CRUDBase):
    def __init__(self):
        super().__init__(User)


crud_user = CRUDUser()