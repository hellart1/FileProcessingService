import uuid
from pathlib import Path
from fastapi import UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from src.services.s3_service import s3_client
from src.services.status_service import StatusService


class FileService(StatusService):
    def __init__(self, file: UploadFile, session: AsyncSession):
        super().__init__()
        self.file = file
        self.session = session
        self.path = self.generate_path()

    def generate_path(self) -> str:
        clean_name = Path(self.file.filename).name
        unique_prefix = uuid.uuid4().hex
        return f'media/{unique_prefix}_{clean_name}'

    async def async_iter_file(self, chunk_size: int = 5 * 1024 * 1024):
        while True:
            chunk = await self.file.read(chunk_size)
            if not chunk:
                break
            yield chunk

    async def upload_to_storage(self):
        return await s3_client.put_concurrent_parts(
            self.async_iter_file,
            self.file.filename
        )

