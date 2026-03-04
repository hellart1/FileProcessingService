from typing import AsyncGenerator, Annotated

from redis.asyncio import Redis
from redis.exceptions import RedisError
from fastapi import Request, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.database import AsyncSessionLocal
from src.services.file_service import FileService
from src.services.status_service import AsyncStatusService


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session

async def get_redis(request: Request) -> Redis:
    if hasattr(request.app.state, 'redis'):
        return await request.app.state.redis
    raise RedisError('Client is not initialized')

DBSessionDep = Annotated[AsyncSession, Depends(get_db)]
RedisDep = Annotated[Redis, Depends(get_redis)]

async def get_file_service(
        db: DBSessionDep,
        redis: RedisDep,
) -> FileService:
    return FileService(db, redis)

async def get_status_service(
        redis: RedisDep
) -> AsyncStatusService:
    return AsyncStatusService(redis)

FileServiceDep = Annotated[FileService, Depends(get_file_service)]
StatusServiceDep = Annotated[AsyncStatusService, Depends(get_status_service)]