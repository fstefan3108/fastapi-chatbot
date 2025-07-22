from app.crud.base import CRUDBase
from app.models.website import Website

crud_website = CRUDBase[Website](Website)