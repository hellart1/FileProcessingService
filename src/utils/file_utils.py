import base64
import logging
import mimetypes
import os

def safe_remove_temp_file(path):
    try:
        if path and os.path.exists(path):
            os.remove(path)
    except Exception as cleanup_error:
        logging.error(f'Failed to remove temp file {path}: {cleanup_error}')

def file_to_base64(img_path):
    with open(img_path, 'rb') as file:
        return base64.b64encode(file.read()).decode('utf-8')

def get_extension(file, content_type=None):
    # magic.from_file
    if content_type:
        ext = mimetypes.guess_extension(content_type)
        if not ext:
            ext = os.path.splitext(file)[1] or '.bin'
    else:
        ext = os.path.splitext(file)[1] or '.bin'

    return ext