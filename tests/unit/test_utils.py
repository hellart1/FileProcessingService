import uuid

from src.utils import get_hash, get_extension

def test_get_hash_returns_uuid():
    result = get_hash()
    assert isinstance(result, uuid.UUID)

def test_get_extension_with_content_type():
    ext = get_extension('dummy', content_type='image/jpeg')
    assert ext in [".jpg", ".jpeg"]

def test_get_extension_by_filename():
    ext = get_extension("document.pdf")
    assert ext == ".pdf"

def test_get_extension_default():
    ext = get_extension('dummy')
    assert ext == ".bin"