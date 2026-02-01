import json
from src.db.redis import redis_client


class StatusService:
    def __init__(self):
        if redis_client is None:
            raise RuntimeError("Redis is not initialized")
        self.redis = redis_client

    @staticmethod
    def _key_status(file_id: str) -> str:
        return f"file_status:{file_id}"

    @staticmethod
    def _key_progress(file_id: str) -> str:
        return f"file_progress:{file_id}"

    async def set_status(self, uuid: str, result: str):
        return await redis_client.set(
            self._key_status(uuid),
            json.dumps(result, ensure_ascii=False),
            ex=3600
        )

    async def set_progress(self, uuid, status, progress):
        return await redis_client.set(
            self._key_progress(uuid),
            json.dumps({
                'status': status,
                'progress': progress
            }, ensure_ascii=False),
            ex=3600
        )

    async def get_status(self, uuid):
        return await redis_client.get(self._key_status(uuid))

    async def get_progress(self, uuid):
        return await redis_client.get(self._key_progress(uuid))