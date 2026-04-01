from fastapi import UploadFile, APIRouter, Depends

from src.db.models import File
from src.api.dependencies import FileServiceDep, StatusServiceDep, get_db, DBSessionDep

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

@router.post('/create')
async def create_file(session: DBSessionDep, json: dict):
    model = File(**json)
    session.add(model)
    await session.commit()
    return {'status': 'ok'}