from typing import AsyncGenerator, Annotated

from redis.asyncio import Redis
from redis.exceptions import RedisError
from fastapi import Request, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.database import AsyncSessionLocal
from src.services.file_service import FileService


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session

async def get_redis(request: Request) -> Redis:
    if not hasattr(request.app.state, "redis_pool"):
        raise RedisError('client is not initialized')
    return Redis(connection_pool=request.app.state.redis_pool)

DBSessionDep = Annotated[AsyncSession, Depends(get_db)]
RedisDep = Annotated[Redis, Depends(get_redis)]

async def get_file_service(
        db: DBSessionDep,
        redis: RedisDep,
) -> FileService:
    return FileService(db, redis)

# Прописать StatusServiceDep для получения результата с редис
FileServiceDep = Annotated[FileService, Depends(get_file_service)]