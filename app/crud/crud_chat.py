from app.models.chat import Chat
from app.crud.base import CRUDBase

class CRUDChat(CRUDBase):
    def __init__(self):
        super().__init__(Chat)


crud_chat = CRUDChat()