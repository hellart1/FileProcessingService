import json
import logging
import os
import tempfile
import redis
from celery.utils.log import get_task_logger

from src.core.config import settings
from src.services.ocr_service import Registry, process_file
from src.services.s3_service import s3_client
from src.utils.file_utils import safe_remove_temp_file
from src.workers.celery_app import celery_app, sync_redis_client
from src.services.status_service import SyncStatusService


status_service = SyncStatusService(sync_redis_client)

logger = get_task_logger(__name__)


@celery_app.task()
def processing_file(s3_key, uuid):
    file_path = None
    logger.info(f'Start processing for {uuid}')
    try:
        file_path = s3_client.download_temp_file(s3_key)

        status_service.set_status(uuid, 'processing', 0)

        logger.info(f'Processing file for {uuid}')
        result = process_file(uuid, file_path, status_service=status_service)

        logger.info(f'Process file finished for {uuid}. Result: {result}')

        status_service.set_result(uuid, result)
        status_service.set_status(uuid, 'done', 100)

        logger.info(f'Task {uuid} completed successfully')
    except Exception as e:
        logger.error(f'Error during processing file: {e}')
        status_service.set_result(uuid, {"error": 'Please try again'})
    finally:
        if file_path:
            safe_remove_temp_file(file_path)
