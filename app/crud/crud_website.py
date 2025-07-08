from app.crud.base import CRUDBase
from app.models.website import Website

class CRUDWebsite(CRUDBase):
    def __init__(self):
        super().__init__(Website)


crud_website = CRUDWebsite()