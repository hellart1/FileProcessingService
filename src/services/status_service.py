import json
import logging

from redis import Redis as SyncRedis
from redis.asyncio import Redis as AsyncRedis

from src.db.database import Scoped_session
from src.db.models import File


class BaseStatusService:
    def __init__(self, redis_client: SyncRedis | AsyncRedis):
        self.redis = redis_client

    @staticmethod
    def _key_result(file_id: str) -> str:
        return f"file_result:{file_id}"

    @staticmethod
    def _key_progress(file_id: str) -> str:
        return f"file_status:{file_id}"


class AsyncStatusService(BaseStatusService):
    async def get_result(self, uuid: str):
        in_cache = await self.redis.get(self._key_result(uuid))

        if in_cache:
            return json.loads(in_cache)

        db = Scoped_session()

        try:
            entity = db.get(File, uuid)
            if entity.result:
                await self.set_result(uuid, entity.result)
                return entity.result
        except Exception as e:
            logging.error(f'error for getting result {e}')

        return {'error': 'make sure processing is complete, try again'}

    async def get_status(self, uuid: str):
        return json.loads(
            await self.redis.get(self._key_progress(uuid))
        )

    async def set_result(self, uuid: str, result: str | dict, ex: int = 3600):
        try:
            await self.redis.set(
                self._key_result(uuid),
                json.dumps(result, ensure_ascii=True),
                ex=ex
            )
        except Exception as e:
            logging.error(f'Error saving result to redis: {e}')

    async def set_status(self, uuid: str, status: str, progress: int, ex: int = 3600):
        return await self.redis.set(
            self._key_progress(uuid),
            json.dumps({
                'status': status,
                'progress': progress
            }, ensure_ascii=False),
            ex=ex
        )


class SyncStatusService(BaseStatusService):
    def set_result(self, uuid: str, result: str | dict, ex: int = 3600):
        db = Scoped_session()
        try:
            entity = db.get(File, uuid)
            if entity:
                entity.result = result
                db.commit()
        except Exception as e:
            logging.error(f'Error saving result to db: {e}')
        finally:
            Scoped_session.remove()

        try:
            self.redis.set(
                self._key_result(uuid),
                json.dumps(result, ensure_ascii=True),
                ex=ex
            )
        except Exception as e:
            logging.error(f'Error saving result to redis: {e}')

    def set_status(self, uuid: str, status: str, progress: int, ex: int = 3600):
        return self.redis.set(
            self._key_progress(uuid),
            json.dumps({
                'status': status,
                'progress': progress
            }, ensure_ascii=False),
            ex=ex
        )
