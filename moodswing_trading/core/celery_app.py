"""Factory for Celery application used by background workers."""

from celery import Celery
from celery.signals import task_failure
from prometheus_client import Counter

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

TASK_FAILURES = Counter(
    "task_failures_total",
    "Total Celery task failures",
    ["task_name"],
)


@task_failure.connect
def _count_failure(sender=None, **_: object) -> None:
    """Increment Prometheus counter when a task fails."""
    name = getattr(sender, "name", str(sender)) if sender else "unknown"
    TASK_FAILURES.labels(name).inc()


setup_periodic_tasks(celery_app)

__all__ = ["celery_app"]