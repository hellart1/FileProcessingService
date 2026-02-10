from redis.asyncio import Redis
from redis.asyncio.connection import ConnectionPool

from src.core.config import settings

redis_client: Redis | None = None

async def init_redis(app):
    pool = ConnectionPool.from_url(
        settings.REDIS_URL,
        decode_responses=True
    )
    app.state.redis_pool = pool


async def close_redis(app):
    if hasattr(app.state, "redis_pool"):
        await app.state.redis_pool.disconnect()