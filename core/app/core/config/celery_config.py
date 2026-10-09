# celery_config.py
from datetime import timedelta

from celery import Celery

from app.core.config.config import settings
from app.core.messaging.message_service import MessageService
from app.db.redis_service import RedisService

# Initialize services
redis_service = RedisService()
message_service = MessageService(redis_service)

# Celery configuration
CELERY_BROKER_URL = settings.CELERY_BROKER_URL or settings.REDIS_URL
CELERY_RESULT_BACKEND = settings.CELERY_RESULT_BACKEND or settings.REDIS_URL

celery_app = Celery(
    "scheduler", broker=CELERY_BROKER_URL, backend=CELERY_RESULT_BACKEND
)

# Celery Configuration
celery_app.conf.update(
    timezone="UTC",
    enable_utc=True,
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    task_track_started=True,
    worker_prefetch_multiplier=1,
)

# Schedule tasks for scheduler production and consumption
celery_app.conf.beat_schedule = {
    "produce-messages": {
        "task": "tasks.produce_messages",
        "schedule": timedelta(seconds=settings.PRODUCE_INTERVAL_SECONDS or 3600),
    },
    "consume-messages": {
        "task": "tasks.consume_messages",
        "schedule": timedelta(seconds=settings.CONSUME_INTERVAL_SECONDS or 60),
    },
}
