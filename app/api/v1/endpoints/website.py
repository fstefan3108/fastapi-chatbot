from fastapi import APIRouter
from starlette import status


from app.crud.crud_website import create_website, get_websites
from app.schemas.website import WebsiteRequest
from app.utils.validation import check_user

from ...deps import db_dependency, user_dependency

### Router Declaration ###
router = APIRouter()


### endpoint for adding websites - takes in request body that comes from streamlit frontend as a pydantic scheme, ###
### db: db_dependency for adding the website to the database and user dependency to authenticate user before creating the website. ###
### after the URL is entered, the scraper function runs, takes in the url sent through streamlit front and saves the scraped content ###
### to a variable. A new website is then created with fields accordingly and gets added to the database at the end. ###

@router.post("/add_website", status_code=status.HTTP_201_CREATED)
async def add_website_endpoint(website: WebsiteRequest, db: db_dependency, user: user_dependency):
    check_user(user=user, status_code=404, detail="User not found.")
    new_website = create_website(website=website, db=db, user=user)
    return new_website



### Fetches all websites for the authenticated user from the db. ###

@router.get("/get_websites", status_code=status.HTTP_200_OK)
async def get_websites_endpoint(db: db_dependency, user: user_dependency):
    check_user(user=user, status_code=404, detail="User not found.")
    websites = get_websites(db=db, user=user) # Calls get_websites() from crud_website #
    return [{"id": website.id, "title": website.title, "url": website.url} for website in websites]