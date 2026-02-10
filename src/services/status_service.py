import json
from redis.asyncio import Redis

class StatusService:
    def __init__(self, redis_client: Redis):
        self.redis = redis_client

    @staticmethod
    def _key_status(file_id: str) -> str:
        return f"file_status:{file_id}"

    @staticmethod
    def _key_progress(file_id: str) -> str:
        return f"file_progress:{file_id}"

    async def set_status(self, uuid: str, result: str):
        return await self.redis.set(
            self._key_status(uuid),
            json.dumps(result, ensure_ascii=False),
            ex=3600
        )

    async def set_progress(self, uuid, status, progress):
        return await self.redis.set(
            self._key_progress(uuid),
            json.dumps({
                'status': status,
                'progress': progress
            }, ensure_ascii=False),
            ex=3600
        )

    async def get_status(self, uuid):
        return await self.redis.get(self._key_status(uuid))

    async def get_progress(self, uuid):
        return await self.redis.get(self._key_progress(uuid))