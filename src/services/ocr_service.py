import logging
from typing import Type, Annotated

import pdf2image
import pytesseract
from PIL import Image, ImageEnhance

from src.db.models import StatusEnum
from src.services.status_service import SyncStatusService
from src.utils.file_utils import get_extension


class BaseHandler:
    def handle(self, file_id, file_path, **kwargs):
        raise NotImplementedError

class Registry:
    handlers: dict[str, BaseHandler] = {}

    @classmethod
    def register(cls, *extensions: str):
        def decorator(handler_cls: Type[BaseHandler]):
            for ext in extensions:
                cls.handlers[ext] = handler_cls()
            return handler_cls
        return decorator

    @classmethod
    def get_handler(cls, file_path):
        ext = get_extension(file_path)
        handler = cls.handlers.get(ext)

        if not handler:
            raise ValueError(f'No handler for {file_path}')

        return handler

@Registry.register('.jpg', '.jpeg', '.png')
class JPEGHandler(BaseHandler):
    def handle(self, file_id, file_path, **kwargs):
        parsed_image = preprocess_image(Image.open(file_path))

        text = pytesseract.image_to_string(parsed_image, lang='rus')

        return {"result": text}

@Registry.register('.pdf')
class PDFHandler(BaseHandler):
    def handle(self, file_id, file_path, **kwargs):
        status_service: SyncStatusService | None = None

        try:
            status_service = kwargs.get('status_service')
        except ValueError as e:
            logging.error('status_service was not submitted')

        images = pdf2image.convert_from_path(file_path, dpi=300)
        total = len(images)

        text = ''
        for i, img in enumerate(images):
            percent = int((i + 1) / total * 100)
            if percent % 10 == 0:
                status_service.set_status(
                    uuid=file_id,
                    status=StatusEnum.processing,
                    progress=percent)

            parsed_img = preprocess_image(img)
            text += pytesseract.image_to_string(parsed_img, lang='rus')

        return {'result': text}

def preprocess_image(img: Type[Image]):
    gray_shade_img = img.convert('L')
    enhancer = ImageEnhance.Contrast(gray_shade_img)
    contrasted_img = enhancer.enhance(2)

    return contrasted_img

def process_file(file_id, file_path, **kwargs):
    handler = Registry.get_handler(file_path)
    return handler.handle(file_id, file_path, **kwargs)