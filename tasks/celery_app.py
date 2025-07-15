from celery import Celery
from app.core.config import settings

celery_app = Celery(
    "tasks",
    broker=settings.redis_url,
    backend=settings.redis_url
)

import tasks.website
import tasks.embedding
