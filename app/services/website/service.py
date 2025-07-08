from fastapi import HTTPException
from sqlalchemy import and_
from sqlalchemy.orm import Session
from app.crud.crud_website import crud_website
from app.models.website import Website
from app.schemas.website import WebsiteRequest
from app.services.website.handle_scraping import handle_scraping
from app.utils.db_transaction import db_transactional
from app.vectorstore.store_embeddings import embed_website_chunks


class WebsiteService:
    def __init__(self, db: Session, user: dict):
        self.db = db
        self.user = user

    @db_transactional
    def create_website(self, website: WebsiteRequest):
        criteria = and_(Website.url == website.url, Website.owner_id == self.user.get("id"))
        existing = crud_website.get_first(db=self.db, criteria=criteria)
        if existing:
            raise HTTPException(status_code=400, detail="Website already exists")

        scraped_website = handle_scraping(website=website)

        values = {
            "url": website.url,
            "owner_id": self.user.get("id"),
            "title": scraped_website["title"],
            "chunks": scraped_website["chunks"],
        }

        new_website = crud_website.create(db=self.db, data=values)
        embed_website_chunks(db=self.db, user_id=self.user.get("id"))

        return new_website


    def get_websites(self):
        criteria = Website.owner_id == self.user.get("id")
        websites = crud_website.get_by(db=self.db, criteria=criteria)
        return websites