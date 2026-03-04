from redis.asyncio import Redis

from src.core.config import settings

redis_client: Redis | None = None

async def init_redis(app):
    app.state.redis = Redis.from_url(
        settings.REDIS_URL,
        decode_responses=True,
        max_connections=20
    )


async def close_redis(app):
    if hasattr(app.state, "redis"):
        await app.state.redis.aclose()