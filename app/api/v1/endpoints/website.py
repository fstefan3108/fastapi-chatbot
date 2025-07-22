from fastapi import APIRouter
from starlette import status
from app.schemas.website import WebsiteCreate, WebsiteRequest
from app.services.website.scrape_and_save_website import scrape_and_store_website
from app.services.website.service import WebsiteService
from app.api.deps import db_dependency, user_dependency

### Router Declaration ###
router = APIRouter()


### endpoint for adding websites - takes in request body that comes from streamlit frontend as a pydantic scheme, ###
### db: db_dependency for adding the website to the database and user dependency to authenticate user before creating the website. ###
### after the URL is entered, the scraper function runs, takes in the url sent through streamlit front and saves the scraped content ###
### to a variable. A new website is then created with fields accordingly and gets added to the database at the end. ###


@router.post("/website", status_code=status.HTTP_202_ACCEPTED)
async def create_website(website: WebsiteRequest, user: user_dependency, db: db_dependency):
    await scrape_and_store_website(url=website.url, user=user, db=db)
    return {"message": "Website created successfully"}


### Fetches all websites for the authenticated user from the db. ###

@router.get("/websites", status_code=status.HTTP_200_OK)
async def get_websites(user: user_dependency, db: db_dependency):
    website_service = WebsiteService(db=db, user=user)
    websites = await website_service.get_websites()
    return websites