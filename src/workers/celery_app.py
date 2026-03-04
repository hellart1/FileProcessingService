import redis
from celery import Celery
from sqlalchemy.orm import scoped_session

from src.core.config import settings
from src.db.database import SyncSessionLocal

celery_app = Celery('workers',
                    broker=settings.RABBITMQ_URL)

celery_app.autodiscover_tasks(['src.workers'])

sync_redis_client = redis.from_url(
    settings.REDIS_URL,
    decode_responses=True,
    max_connections=20
)
