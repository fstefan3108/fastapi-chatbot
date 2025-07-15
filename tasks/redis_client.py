from redis import Redis
from app.core.config import settings

def get_redis() -> Redis:
    return Redis.from_url(settings.redis_url)

r = get_redis()