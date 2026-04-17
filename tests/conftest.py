import pytest
import fakeredis

from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from src.services.file_service import FileService
from src.core.config import settings
from src.db.database import Base
from src.main import app
from src.api.dependencies import get_db, get_redis, get_file_service

DATABASE_URL = "sqlite+aiosqlite:///:memory:"

test_engine = create_async_engine(DATABASE_URL, echo=True)
TestAsyncSession = async_sessionmaker(test_engine, class_=AsyncSession)

@pytest.fixture(autouse=True)
async def create_tables():
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest.fixture
async def db_session():
    async with TestAsyncSession() as session:
        yield session

@pytest.fixture
async def fake_redis():
    redis = fakeredis.aioredis.FakeRedis(decode_responses=True)
    yield redis
    await redis.aclose()

@pytest.fixture
def override_app(db_session, fake_redis):
    app.dependency_overrides[get_db] = db_session
    app.dependency_overrides[get_redis] = fake_redis
    # app.dependency_overrides[get_file_service] = lambda: FileService(db_session, fake_redis)
    return app

@pytest.fixture
def client(override_app):
    return TestClient(override_app)