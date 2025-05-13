from redis.asyncio import Redis

from .config import settings

common = Redis.from_url(settings.REDIS_URL, db=0, decode_responses=True)

# For closing connections in the app lifespan (main.py)
connections = (common,)
