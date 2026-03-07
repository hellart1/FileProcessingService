import os.path
import uuid
from pathlib import Path
from typing import AsyncGenerator
from uuid import UUID

from fastapi import UploadFile, HTTPException
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from src.services.s3_service import s3_client
from src.services.status_service import AsyncStatusService
from src.db.models import File
from src.utils import get_hash
from src.workers.tasks import processing_file


class FileService:
    def __init__(self, session: AsyncSession, redis: Redis):
        self.session = session
        self.status = AsyncStatusService(redis)

    async def process_file(self, file: UploadFile) -> UUID:
        """ Create delayed task in Broker """
        self.check_mime_type(file)

        file_hash = get_hash()
        file_path = self.generate_path(file)

        await self.upload_to_storage(file, file_path)
        await self.status.set_status(file_hash, 'uploaded', 0)

        await self.create_file_metadata(file, file_hash, file_path)

        processing_file.delay(file_path, file_hash)

        return file_hash

    @staticmethod
    def generate_path(file: UploadFile) -> str:
        clean_name = Path(file.filename).name
        unique_prefix = uuid.uuid4().hex
        return f'media/{unique_prefix}_{clean_name}'

    @staticmethod
    async def async_iter_file(file: UploadFile, chunk_size: int = 5 * 1024 * 1024) -> AsyncGenerator[bytes | None, None]:
        while True:
            chunk = await file.read(chunk_size)
            if not chunk:
                break
            yield chunk

    @staticmethod
    def check_mime_type(file: UploadFile) -> None:
        allowed_extensions = ['.jpg', '.pdf', '.png']
        if os.path.splitext(file.filename)[1].lower() not in allowed_extensions:
            raise HTTPException(status_code=400, detail={
                'error': f'Unsupported file extension. Please use one of them: {allowed_extensions}'
            })

    async def upload_to_storage(self, file: UploadFile, path: str):
        return await s3_client.put_concurrent_parts(
            self.async_iter_file(file),
            path
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