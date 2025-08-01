from pydantic import HttpUrl
from sqlalchemy.ext.asyncio import AsyncSession
from app.crud.crud_website import crud_website
from app.models import User
from app.models.website import Website
from app.schemas.website import WebsiteCreate, WebsiteRequest
from app.utils.db_transaction import db_transactional_async


class WebsiteService:
    def __init__(self, db: AsyncSession, user: User):
        self.db = db
        self.user = user

    async def get_websites(self) -> list[Website]:
        websites = await crud_website.get_all(db=self.db, criteria=Website.owner_id == self.user.id)
        return websites

    @db_transactional_async
    async def create_website(self, title: str, url: HttpUrl) -> Website:
        website_create = WebsiteCreate(
            **WebsiteRequest(url=url).model_dump(),
            title=title,
            owner_id=self.user.id
        )

        data_dict = website_create.model_dump()
        data_dict["url"] = str(data_dict["url"])

        new_website = await crud_website.create(db=self.db, data=data_dict)
        return new_website

    async def get_website_by_id(self, id: int) -> Website:
        website = await crud_website.get_single(db=self.db, criteria=Website.id == id)
        return website

    @db_transactional_async
    async def delete_website_by_id(self, id: int) -> None:
        await crud_website.delete(db=self.db, criteria=(Website.id == id) & (Website.owner_id == self.user.id))

    @db_transactional_async
    async def delete_all_websites(self) -> None:
        await crud_website.delete(db=self.db, criteria=(Website.owner_id == self.user.id))