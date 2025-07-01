from fastapi import HTTPException

from app.api.deps import db_dependency, user_dependency
from app.schemas.website import WebsiteRequest
from app.services.scrape.scrape_website import scrape_website


def handle_scraping_and_embedding(website: WebsiteRequest, db: db_dependency, user: user_dependency):
    # scrape website #
    try:
        scraped_website = scrape_website(website.url)

    except Exception as error:
        raise HTTPException(status_code=404, detail=f"Scrapping failed: {str(error)}")

    return scraped_website