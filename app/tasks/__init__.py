from celery import Celery
from celery.schedules import crontab
from app.config import get_settings

settings = get_settings()

celery_app = Celery(
    "news_aggregator",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=["app.tasks.fetch_articles"]
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
    "periodic-article-fetch": {
        "task": "fetch_all_sources",
        "schedule": crontab(minute=f"*/{settings.FETCH_INTERVAL_MINUTES}"),
    },
}

# The 'include' parameter above handles task discovery
