"""Daily Postgres partition maintenance via pg_partman."""

from __future__ import annotations

from sqlalchemy import text

from moodswing_trading.core.celery_app import celery_app
from moodswing_trading.core.logging import setup_logging
from db.models import engine

setup_logging()


@celery_app.task(name="partition_maintenance")
def run() -> None:
    """Invoke pg_partman maintenance procedure."""
    with engine.begin() as conn:
        conn.execute(text("SELECT partman.run_maintenance();"))