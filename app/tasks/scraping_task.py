import asyncio
from celery import Celery
from app.core.config import settings
from app.services.website.scrape_and_save_website import scrape_and_store_website

celery_app = Celery("scraper", broker=settings.redis_url, backend=settings.redis_url)

celery_app.config_from_object({
    'broker_url': 'redis://localhost:6379/0',
    'result_backend': 'redis://localhost:6379/0',
    'task_serializer': 'json',
    'accept_content': ['json'],
    'result_serializer': 'json',
    'timezone': 'UTC',
    'enable_utc': True,
})

@celery_app.task(bind=True, max_retries=3, name='scrape_website_task')
def scrape_website_task(self, url: str, user_id: int):
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            return loop.run_until_complete(
                scrape_and_store_website(url=url, user_id=user_id)
            )
        finally:
            loop.close()
    except Exception as e:
        print(f"[ERROR] Task Failed (attempt {self.request.retries + 1}/{self.max_retries}): {e}")
        raise self.retry(exc=e, max_retries=3)
