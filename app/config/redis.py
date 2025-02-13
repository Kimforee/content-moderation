import aioredis
import os

REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379")

redis = None  # Global Redis instance

async def get_redis():
    """
    Initializes and returns a Redis connection.
    """
    global redis
    if redis is None:
        redis = await aioredis.from_url(REDIS_URL, decode_responses=True)
    return redis
