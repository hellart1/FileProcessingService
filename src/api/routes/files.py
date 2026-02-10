import json
import uuid
from typing import Annotated

import aiofiles
from fastapi import FastAPI, Depends, UploadFile, APIRouter
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.responses import StreamingResponse

from src.db.redis import init_redis, close_redis
from src.db import redis
from src.db.database import engine, Base
from src.db.models import File
from src.services.file_service import FileService
from src.services.s3_service import s3_client
from src.workers.tasks import processing_file
from src.api.dependencies import DBSessionDep, RedisDep, FileServiceDep

router = APIRouter(tags=['Работа с файлами'])

async def aiterfile(file: UploadFile, chunk_size: int = 5 * 1024 * 1024):
    while True:
        chunk = await file.read(chunk_size)
        if not chunk:
            break
        yield chunk

@router.post('/files')
async def upload_file(
        uploaded_file: UploadFile,
        file_service: FileServiceDep
):
    await file_service.process_file(uploaded_file)
    return {'status': 'ok'}
    # await s3_client.put_concurrent_parts(
    #     aiterfile(uploaded_file),
    #     uploaded_file.filename
    # )
    # s3_key = f"media/{uploaded_file.filename}"
    # file_id = uuid.uuid4()
    #
    # new_file = File(
    #     id=file_id,
    #     filename=uploaded_file.filename,
    #     content_type=uploaded_file.content_type,
    #     size=uploaded_file.size,
    #     s3_path=s3_key
    # )
    # session.add(new_file)
    # await session.commit()
    #
    # processing_file.delay(s3_key, str(file_id))
    #
    # return {'status': 'ok', 'key': str(file_id)}

# StatusServiceDep
@router.get('/files/{file_id}/status')
async def get_file_status(file_id: str, redis_client: RedisDep):
    data = json.loads(await redis_client.get(file_id))
    return data

@router.get('/files/{file_id}/result')
async def get_file_result(file_id: str, redis_client: RedisDep):
    data = json.loads(await redis_client.get(f"{file_id}:result"))
    return data

@router.post('/setup_database')
async def setup_database():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

@router.get('/users')
async def read_users(session: DBSessionDep):
    stmt = select(File)
    result = await session.execute(stmt)
    return result.scalars().all()

@router.post('/stream')
async def streaming(uploaded_file: UploadFile):
    await s3_client.upload_file_async(uploaded_file, uploaded_file.filename)
