import uuid
from pathlib import Path
from uuid import UUID

from fastapi import UploadFile
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from src.services.s3_service import s3_client
from src.services.status_service import StatusService
from src.db.models import File
from src.utils import get_hash
from src.workers.tasks import processing_file


class FileService(StatusService):
    def __init__(self, session: AsyncSession, redis: Redis):
        super().__init__(redis_client=redis)
        self.session = session

    async def process_file(self, file: UploadFile):
        file_hash = get_hash()
        file_path = self.generate_path(file)

        await self.upload_to_storage(file)
        await self.set_status(file_hash, 'uploaded')

        await self.create_file_metadata(file, file_hash, file_path)

        processing_file.delay(file_path, file_hash)

        return self.get_status

    @staticmethod
    def generate_path(file: UploadFile) -> str:
        clean_name = Path(file.filename).name
        unique_prefix = uuid.uuid4().hex
        return f'media/{unique_prefix}_{clean_name}'

    @staticmethod
    async def async_iter_file(file: UploadFile, chunk_size: int = 5 * 1024 * 1024):
        while True:
            chunk = await file.read(chunk_size)
            if not chunk:
                break
            yield chunk

    async def upload_to_storage(self, file: UploadFile):
        return await s3_client.put_concurrent_parts(
            self.async_iter_file,
            file.filename
        )

    async def create_file_metadata(self, file: UploadFile, f_hash: UUID, path: str):
        new_file = File(
            id=f_hash,
            filename=file.filename,
            content_type=file.content_type,
            size=file.size,
            s3_path=path
        )
        self.session.add(new_file)
        await self.session.commit()