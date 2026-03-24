"""
Celery Configuration

Task queue for scheduled ETL and background jobs.
"""

from celery import Celery
from datetime import timedelta
import logging

from src.core.config import get_settings

logger = logging.getLogger(__name__)

settings = get_settings()


def make_celery():
    """Create Celery app with configuration"""
    celery_app = Celery(
        "epidemiology",
        broker=(
            settings.REDIS_URL
            if hasattr(settings, "REDIS_URL")
            else "redis://localhost:6379/0"
        ),
        backend=(
            settings.REDIS_URL
            if hasattr(settings, "REDIS_URL")
            else "redis://localhost:6379/0"
        ),
        include=["src.services.tasks"],
    )

    celery_app.conf.update(
        task_serializer="json",
        accept_content=["json"],
        result_serializer="json",
        timezone="UTC",
        enable_utc=True,
        task_track_started=True,
        task_time_limit=3600,
        worker_prefetch_multiplier=1,
        beat_schedule={
            "ingest-daily-weather": {
                "task": "tasks.ingest_weather_data",
                "schedule": timedelta(hours=6),
            },
            "ingest-digital-signals": {
                "task": "tasks.ingest_digital_signals",
                "schedule": timedelta(days=1),
            },
            "generate-daily-predictions": {
                "task": "tasks.generate_predictions",
                "schedule": timedelta(days=1),
            },
        },
    )

    return celery_app


celery_app = make_celery()
