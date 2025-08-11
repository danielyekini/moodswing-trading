"""Daily Postgres maintenance (no pg_partman).

For native LIST partitioned parents with DEFAULT partitions, there is little to
"maintain". This task is kept as a placeholder to perform optional hygiene like
ANALYZE/VACUUM or index refreshes if needed in the future.
"""

from __future__ import annotations

from sqlalchemy import text

from moodswing_trading.core.celery_app import celery_app
from moodswing_trading.core.logging import setup_logging
from db.models import engine

setup_logging()


@celery_app.task(name="partition_maintenance")
def run() -> None:
    """No-op placeholder: run basic VACUUM ANALYZE on partitioned parents."""
    with engine.begin() as conn:
        conn.execute(text("VACUUM (ANALYZE) article;"))
        conn.execute(text("VACUUM (ANALYZE) sentiment_day;"))
        conn.execute(text("VACUUM (ANALYZE) prediction;"))