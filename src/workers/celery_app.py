from celery import Celery

from src.core.config import settings

celery_app = Celery('workers',
                    broker=settings.RABBITMQ_URL)

celery_app.autodiscover_tasks(['src.workers'])
