import json
from fastapi import APIRouter, HTTPException
from starlette import status
from app.schemas.website import WebsiteRequest
from app.services.website.service import WebsiteService
from tasks.website import scrape_add_website_task
from ...deps import db_dependency, user_dependency
from tasks.redis_client import r

### Router Declaration ###
router = APIRouter()


### endpoint for adding websites - takes in request body that comes from streamlit frontend as a pydantic scheme, ###
### db: db_dependency for adding the website to the database and user dependency to authenticate user before creating the website. ###
### after the URL is entered, the scraper function runs, takes in the url sent through streamlit front and saves the scraped content ###
### to a variable. A new website is then created with fields accordingly and gets added to the database at the end. ###


@router.post("/website", status_code=status.HTTP_202_ACCEPTED)
async def create_website(website: WebsiteRequest, user: user_dependency):
    task = scrape_add_website_task.delay(website.url, user.get("id"))
    return { "message": "Website creation started", "task_id": task.id }


### Fetches all websites for the authenticated user from the db. ###

@router.get("/websites", status_code=status.HTTP_200_OK)
async def get_websites(db: db_dependency, user: user_dependency):
    website_service = WebsiteService(db=db, user=user)
    websites = await website_service.get_websites()
    return websites



@router.get("/task-status/{task_id}", status_code=200)
async def get_task_status(task_id: str):
    data = r.get(task_id)
    if not data:
        raise HTTPException(status_code=404, detail="Task ID not found or expired.")
    return json.loads(data)