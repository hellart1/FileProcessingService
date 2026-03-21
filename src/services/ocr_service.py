import logging

from openai import OpenAI

from src.core.config import settings
from src.utils import file_to_base64

class OCRService:
    """Choose between API requests to LLM or local preinstalled OCR"""
    def __init__(self, llm_api_url: str = settings.LLM_API_URL):
        self.llm_api_url = llm_api_url

    def text_extractor_from_image(self, img_path: str):
        llm = OpenAI(
            api_key='lm-studio',
            base_url=self.llm_api_url
        )

        base64_str = file_to_base64(img_path)
        payload = f"data:image/jpeg;base64,{base64_str}"

        try:
            response = llm.chat.completions.create(
                model='lm-studio',
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "image_url", "image_url": {"url": payload}}
                        ]
                    }
                ]
            )
        except Exception as e:
            logging.error(f'llm is not connected: {e}')
            raise e
        return response.choices[0].message.content

ocr_service = OCRService()