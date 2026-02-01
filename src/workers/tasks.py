import json
import logging
import os
import tempfile
import redis
from celery.utils.log import get_task_logger

from src.core.config import settings
from src.services.s3_service import S3Service
from src.utils.process_pdf import process_pdf
from src.utils.set_progress import set_progress
from src.workers.celery_app import celery_app

redis_client = redis.Redis.from_url(
    settings.REDIS_URL,
    decode_responses=True,
    socket_timeout=5
)

logger = get_task_logger(__name__)

@celery_app.task
def processing_file(s3_key, uuid):
    temp_path = None
    logger.info(f'Start processing for {uuid}')
    try:
        with tempfile.NamedTemporaryFile(prefix='.pdf', delete=False) as temp_file:
            temp_path = temp_file.name
            logger.info(f'Downloading file to {temp_path}')
            S3Service().download_file_sync(s3_key, temp_path)

        set_progress(uuid, 'processing', 0, redis_client)

        logger.info(f'Processing PDF for {uuid}')
        result = process_pdf(temp_path)

        logger.info(f'Process PDF finished for {uuid}. Result: {result}')

        redis_client.set(f"{uuid}:result", json.dumps(result, ensure_ascii=False), ex=3600)
        set_progress(uuid, 'done', 100, redis_client)
        logger.info(f'Task {uuid} completed successfully')
    except Exception as e:
        logging.error('Error during processing file: ', e)
        redis_client.set(uuid, json.dumps({'status': 'error', 'error': str(e)}, ensure_ascii=False))
    finally:
        try:
            if 'temp_path' in locals() and os.path.exists(temp_path):
                os.remove(temp_path)
                logging.info("Temporary file removed")
        except Exception as cleanup_error:
            logging.error(f'Failed to remove temp file {temp_path}: {cleanup_error}')
