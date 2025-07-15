from sqlalchemy.ext.asyncio import AsyncSession
from app.crud.crud_website import crud_website
from app.models.website import Website


class WebsiteService:
    def __init__(self, db: AsyncSession, user: dict):
        self.db = db
        self.user = user

    async def get_websites(self):
        criteria = Website.owner_id == self.user.get("id")
        websites = await crud_website.get_by(db=self.db, criteria=criteria)
        return websites