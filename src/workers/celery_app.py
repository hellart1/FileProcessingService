import redis
from celery import Celery
from src.core.config import settings

celery_app = Celery('workers',
                    broker=settings.RABBITMQ_URL)

celery_app.autodiscover_tasks(['src.workers'])

sync_redis_client = redis.from_url(
    settings.REDIS_URL,
    decode_responses=True,
    max_connections=20
)
