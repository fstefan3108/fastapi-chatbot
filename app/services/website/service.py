from sqlalchemy.ext.asyncio import AsyncSession
from app.crud.crud_website import crud_website
from app.models import User
from app.models.website import Website
from app.schemas.website import WebsiteCreate


class WebsiteService:
    def __init__(self, db: AsyncSession, user: User):
        self.db = db
        self.user = user

    async def get_websites(self) -> list[Website]:
        criteria = Website.owner_id == self.user.id
        websites = await crud_website.get_by(db=self.db, criteria=criteria)
        return websites

    async def create_website(self, title: str, url: str, markdown: list[str]) -> Website:
        website_create = WebsiteCreate(
            title=title,
            url=url,
            markdown=markdown,
            owner_id=self.user.id
        )

        new_website = await crud_website.create(db=self.db, data=website_create.model_dump())
        return new_website

    async def get_website_by_id(self, id: int) -> Website:
        criteria = Website.id == id
        website = await crud_website.get_by(db=self.db, criteria=criteria)
        return website