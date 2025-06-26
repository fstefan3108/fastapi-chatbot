from fastapi import APIRouter, HTTPException
from starlette import status

from app.core.security import check_user
from app.crud.crud_website import create_website, get_websites
from app.schemas.website import WebsiteRequest
from app.services.scrape.scrape_website import scrape_website
from app.vectorstore.chroma_client import embed_website_chunks

from ...deps import db_dependency, user_dependency

### Router Declaration ###
router = APIRouter()


### endpoint for adding websites - takes in request body that comes from streamlit frontend as a pydantic scheme, ###
### db: db_dependency for adding the website to the database and user dependency to authenticate user before creating the website. ###
### after the URL is entered, the scraper function runs, takes in the url sent through streamlit front and saves the scraped content ###
### to a variable. A new website is then created with fields accordingly and gets added to the database at the end. ###

@router.post("/add_website", status_code=status.HTTP_201_CREATED)
async def add_website_endpoint(website: WebsiteRequest, db: db_dependency, user: user_dependency):
    check_user(user)

    # scrape website #
    try:
        scraped_website = scrape_website(website.url)
    except Exception as error:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Scrapping failed: {str(error)}")


    new_website = create_website(website=website, db=db, user=user, scraped_website=scraped_website) # Calls create_website() from crud_website #


    # Embeds website data as an embedding for chromadb #
    user_id = user.get("id")
    embed_website_chunks(db, user_id)

    return new_website



### Fetches all websites for the authenticated user from the db. ###

@router.get("/get_websites", status_code=status.HTTP_200_OK)
async def get_websites_endpoint(db: db_dependency, user: user_dependency):
    check_user(user)

    websites = get_websites(db=db, user=user) # Calls get_websites() from crud_website #
    return [{"id": website.id, "title": website.title, "url": website.url} for website in websites]