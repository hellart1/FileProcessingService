import pytest
from src.services.status_service import AsyncStatusService

@pytest.mark.asyncio
async def test_get_and_set_status(fake_redis):
    service = AsyncStatusService(fake_redis)
    uuid = "random"
    await service.set_status(uuid, "processing", 50)
    data = await service.get_status(uuid)
    assert data == {"status": "processing", "progress": 50}

@pytest.mark.asyncio
async def test_get_and_set_result(fake_redis):
    service = AsyncStatusService(fake_redis)
    uuid = "random"
    await service.set_result(uuid, "result")
    data = await service.get_result(uuid)
    assert data == "result"