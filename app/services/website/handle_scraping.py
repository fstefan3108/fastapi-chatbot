from fastapi import HTTPException
from app.schemas.website import WebsiteRequest
from app.services.scrape.scrape_website import scrape_website


def handle_scraping(website: WebsiteRequest):
    # scrape website #
    try:
        scraped_website = scrape_website(website.url)

    except Exception as error:
        raise HTTPException(status_code=404, detail=f"Scrapping failed: {str(error)}")

    return scraped_website