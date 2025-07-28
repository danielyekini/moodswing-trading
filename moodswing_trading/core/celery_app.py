"""Factory for Celery application used by background workers."""

from celery import Celery

from .config import get_settings
from .scheduler import setup_periodic_tasks

settings = get_settings()

celery_app = Celery(
    "moodswing_trading",
    broker=settings.celery_broker,
    backend=settings.celery_backend,
)

celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="UTC",
    enable_utc=True,
)

setup_periodic_tasks(celery_app)

__all__ = ["celery_app"]