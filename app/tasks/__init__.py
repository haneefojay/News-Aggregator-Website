from celery import Celery
from celery.schedules import crontab
from app.config import get_settings

settings = get_settings()

celery_app = Celery(
    "news_aggregator",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=3600,
)

# Schedule periodic tasks
celery_app.conf.beat_schedule = {
    "fetch-articles-every-15-minutes": {
        "task": "app.tasks.fetch_articles.fetch_all_sources",
        "schedule": crontab(minute=f"*/{settings.FETCH_INTERVAL_MINUTES}"),
    },
}

# Import tasks so Celery can find them
import app.tasks.fetch_articles
