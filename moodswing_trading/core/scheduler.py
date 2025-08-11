"""Register periodic tasks for Celery beat."""

from celery import Celery
from celery.schedules import crontab


def setup_periodic_tasks(app: Celery) -> None:
    """Configure the Celery beat schedule for hourly jobs."""
    app.conf.beat_schedule = {
        "hourly-news-ingest": {
            "task": "hourly_news_ingest",
            "schedule": crontab(minute=0, hour="*"),
        },
        "hourly-sentiment-refresh": {
            "task": "hourly_sentiment_refresh",
            "schedule": crontab(minute=0, hour="*"),
        },
        "hourly-predict": {
            "task": "hourly_predict",
            "schedule": crontab(minute=0, hour="0-20"),
            "args": ("HOURLY",),
        },
        "eod-predict": {
            "task": "hourly_predict",
            "schedule": crontab(minute=5, hour=21),
            "args": ("EOD",),
        },
        "partition-maintenance": {
            "task": "partition_maintenance",
            "schedule": crontab(minute=0, hour=2),
        },
        # "export-cold-partitions": {
        #     "task": "export_cold_partitions",
        #     "schedule": crontab(minute=30, hour=3),
        # },
        "cache-housekeeping": {
            "task": "cache_housekeeping",
            "schedule": crontab(minute=0, hour=4),
        },
    }

__all__ = ["setup_periodic_tasks"]