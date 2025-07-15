from app.core.logger import logger
from app.crud.crud_website import crud_website
from app.db.sync_session import SessionLocal
from tasks.embedding import store_embeddings_task
from tasks.status import update_task_status
from app.services.scrape.scrape_website import Scraper
from tasks.celery_app import celery_app


@celery_app.task(name="scrape_add_website_task")
def scrape_add_website_task(url: str, user_id: int):

    # scraper instantiation #
    scraper = Scraper(url)

    task_id = scrape_add_website_task.request.id
    update_task_status(task_id, "scraping")
    logger.info(f"[START] Task started for user_id={user_id}, url={url}")

    db = SessionLocal()
    try:

        logger.info(f"[STEP 1] Scraping website: {url}")
        result = scraper.scrape()
        data = { **result, "owner_id": user_id }

        logger.info(f"[STEP 2] Scraping complete. Title: {result.get('title')}")
        logger.info("[STEP 3] Storing scraped data to the database")

        new_website = crud_website.create_sync(db, data)
        logger.info(f"[SUCCESS] Website {new_website.id} stored for user {user_id}")
        db.commit()

        update_task_status(task_id, "succeeded", result={"website_id": new_website.id})

        logger.info("[STEP 4] Starting embedding task... ")
        store_embeddings_task.delay(user_id)
        logger.info("Finished embedding task.")

        return {"message": "Website stored", "website_id": new_website.id}

    except Exception as e:
        db.rollback()
        logger.exception(f"Failed to scrape and store website {e}", exc_info=True)
        update_task_status(task_id, "failed", result={"error": str(e)})
        raise e

    finally:
        db.close()