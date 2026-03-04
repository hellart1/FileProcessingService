from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from src.db.redis import init_redis, close_redis
from src.api.routes.files import router as file_router


@asynccontextmanager
async def redis_lifespan(app_instance: FastAPI):
    await init_redis(app_instance)
    yield
    await close_redis(app_instance)

app = FastAPI(lifespan=redis_lifespan)

app.include_router(file_router, prefix='/api/v1')

if __name__ == "__main__":
    uvicorn.run("main:app", reload=True)