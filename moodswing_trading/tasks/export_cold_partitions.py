"""Export partitions older than 36 months to S3 as Parquet files."""

from __future__ import annotations

from datetime import datetime, timedelta
import io

import boto3
import pandas as pd
from sqlalchemy import text

from moodswing_trading.core.celery_app import celery_app
from moodswing_trading.core.logging import setup_logging
from moodswing_trading.core.config import get_settings
from db.models import engine

setup_logging()
settings = get_settings()

s3_client = boto3.client("s3")
BUCKET = settings.tickers_env.lower() + "-archive"


@celery_app.task(name="export_cold_partitions")
def run() -> None:
    """Dump partitions older than 36 months to S3 and drop them."""

    cutoff = datetime.utcnow() - timedelta(days=36 * 30)
    with engine.begin() as conn:
        partitions = conn.execute(
            text("SELECT schemaname, tablename FROM partman.show_partitions('public.article')")
        ).fetchall()
        for schema, table in partitions:
            info = conn.execute(
                text(
                    "SELECT child_start_time FROM partman.show_partition_info(:tbl)"
                ),
                {"tbl": f"{schema}.{table}"},
            )
            # fetchone returns tuple
            start_time = info.fetchone()[0] if info else None
            if start_time and start_time < cutoff:
                df = pd.read_sql_table(table, engine, schema=schema)
                buffer = io.BytesIO()
                df.to_parquet(buffer, index=False)
                buffer.seek(0)
                key = f"{table}.parquet"
                s3_client.upload_fileobj(buffer, BUCKET, key)
                conn.execute(text(f"DROP TABLE {schema}.\"{table}\""))