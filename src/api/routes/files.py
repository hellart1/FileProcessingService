import json

from fastapi import UploadFile, APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from typing import Annotated

from src.db.database import Base, async_engine
from src.api.dependencies import FileServiceDep, StatusServiceDep, get_db
from src.db.models import File

router = APIRouter(tags=['Работа с файлами'])

@router.post('/files')
async def upload_file(
        uploaded_file: UploadFile,
        file_service: FileServiceDep
):
    key = await file_service.process_file(uploaded_file)
    return {'status': 'ok', 'key': key}

@router.get('/files/{file_id}/status')
async def get_file_status(file_id: str, status_service: StatusServiceDep):
    return await status_service.get_status(file_id)

@router.get('/files/{file_id}/result')
async def get_file_result(file_id: str, status_service: StatusServiceDep):
    return await status_service.get_result(file_id)

# @router.get('/files/{file_id}/eee')
# async def get_file_result(file_id: str, db: Annotated[AsyncSession, Depends(get_db)]):
#     file = await db.get(File, file_id)
#
#     return file.result

@router.post('/setup_database')
async def setup_database():
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
