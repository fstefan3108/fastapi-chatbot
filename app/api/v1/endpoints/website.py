from fastapi import APIRouter
from starlette import status

from app.schemas.task import TaskResponse
from app.schemas.website import WebsiteRequest, WebsiteResponse
from app.services.website.service import WebsiteService
from app.api.deps import db_dependency, user_dependency
from app.tasks.scraping_task import scrape_website_task, celery_app

### Router Declaration ###
router = APIRouter()

### endpoint for adding websites - takes in request body that comes from streamlit frontend as a pydantic scheme, ###
### db: db_dependency for adding the website to the database and user dependency to authenticate user before creating the website. ###
### after the URL is entered, the scraper function runs, takes in the url sent through streamlit front and saves the scraped content ###
### to a variable. A new website is then created with fields accordingly and gets added to the database at the end. ###


@router.post("", status_code=status.HTTP_202_ACCEPTED, response_model=TaskResponse)
async def create_website(website: WebsiteRequest, user: user_dependency):
    website_task = scrape_website_task.delay(url=str(website.url), user_id=user.id)
    return {"task_id": website_task.id, "status": "started"}

@router.get("/task/{task_id}", status_code=status.HTTP_200_OK)
async def get_task_status(task_id: str):
    task = celery_app.AsyncResult(task_id)
    return {
        "task_id": task_id,
        "status": task.status,
        "result": task.result if task.ready() else None,
        "error": str(task.traceback) if task.failed() else None
    }

@router.get("", status_code=status.HTTP_200_OK, response_model=list[WebsiteResponse])
async def get_websites(user: user_dependency, db: db_dependency):
    website_service = WebsiteService(db=db, user_id=user.id)
    websites = await website_service.get_websites()
    return [WebsiteResponse.model_validate(site) for site in websites]

@router.delete("/{website_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_website(website_id: int, user: user_dependency, db: db_dependency):
    website_service = WebsiteService(db=db, user_id=user.id)
    await website_service.delete_website_by_id(id=website_id)

@router.delete("", status_code=status.HTTP_204_NO_CONTENT)
async def delete_websites(user: user_dependency, db: db_dependency):
    website_service = WebsiteService(db=db, user_id=user.id)
    await website_service.delete_all_websites()