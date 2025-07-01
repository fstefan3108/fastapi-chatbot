from app.api.deps import db_dependency, user_dependency
from app.crud.base import create, get_by
from app.models.website import Website
from app.schemas.website import WebsiteRequest
from app.services.handle_scraping import handle_scraping_and_embedding
from app.utils.db_transaction import db_transactional
from app.vectorstore.store_embeddings import embed_website_chunks

@db_transactional
def create_website(website: WebsiteRequest, db: db_dependency, user: user_dependency):
    scraped_website = handle_scraping_and_embedding(website=website, db=db, user=user)
    values = {
        "url": website.url,
        "owner_id": user.get("id"),
        "title": scraped_website["title"],
        "chunks": scraped_website["chunks"],
    }

    website = create(model=Website, db=db, data=values)

    embed_website_chunks(db=db, user_id=user.get("id"))
    return website

def get_websites(db: db_dependency, user: user_dependency):
    criteria = Website.owner_id == user.get("id")
    websites = get_by(model=Website, db=db, criteria=criteria)
    return websites

