import io
import pytest
from fastapi import UploadFile, HTTPException
from sqlalchemy import select
from starlette.datastructures import Headers

from src.services.file_service import FileService
from src.db.models import File
from src.api.dependencies import FileServiceDep, DBSessionDep
from src.utils import get_hash

@pytest.fixture
def file_service(db_session, fake_redis):
    return FileService(db_session, fake_redis)

def test_check_mime_type_valid(file_service):
    dummy_file = io.BytesIO(b"content")
    valid_file = UploadFile(file=dummy_file, filename="document.pdf")
    file_service.check_mime_type(valid_file)

def test_check_mime_type_invalid(file_service):
    dummy_file = io.BytesIO(b"content")
    invalid_file = UploadFile(file=dummy_file, filename="script.exe")
    with pytest.raises(HTTPException) as exc:
        file_service.check_mime_type(invalid_file)
    assert exc.value.status_code == 400

def test_generate_path(file_service):
    dummy_file = io.BytesIO(b"content")
    file = UploadFile(file=dummy_file, filename="photo.jpg")
    path = file_service.generate_path(file)
    assert path.startswith("tmp/")
    assert path.endswith("_photo.jpg")

@pytest.mark.asyncio
async def test_create_file_metadata(file_service, db_session):
    dummy_file = io.BytesIO(b"content")
    file = UploadFile(
        file=dummy_file,
        filename="document.pdf",
        size=50,
        headers=Headers({"content-type": "application/pdf"})
    )
    f_hash = get_hash()
    path = "tmp/document.pdf"
    await file_service.create_file_metadata(file, f_hash, path)

    stmt = select(File).where(File.filename == "document.pdf")
    res = await db_session.execute(stmt)
    assert res.one_or_none() is not None