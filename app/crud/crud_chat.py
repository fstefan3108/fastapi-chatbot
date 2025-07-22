from app.models.chat import Chat
from app.crud.base import CRUDBase

crud_chat = CRUDBase[Chat](Chat)