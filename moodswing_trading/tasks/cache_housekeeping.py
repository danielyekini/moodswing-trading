"""Periodic cache housekeeping for Redis keys and lists."""

from __future__ import annotations

import os
import redis

from moodswing_trading.core.celery_app import celery_app
from moodswing_trading.core.logging import setup_logging
from moodswing_trading.core.config import get_settings


setup_logging()
settings = get_settings()

REDIS = redis.Redis.from_url(settings.redis_url)


@celery_app.task(name="cache_housekeeping")
def run() -> None:
    """Trim dead letter queues and purge temporary keys.

    This keeps memory usage bounded and removes stale artifacts.
    """

    # Trim Celery dead letter list (if any)
    try:
        REDIS.ltrim("celery:dead_letter", -1000, -1)
    except Exception:
        pass

    # Remove temporary/debug keys
    try:
        for key in REDIS.scan_iter("tmp:*"):
            try:
                REDIS.delete(key)
            except Exception:
                pass
    except Exception:
        pass








