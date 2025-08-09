from __future__ import annotations

from sqlalchemy import text
from sqlalchemy.engine import Engine


def ensure_default_partitions(engine: Engine) -> None:
    """Create default partitions for partitioned tables if missing.

    This is a defensive runtime safeguard to avoid INSERT failures like:
    "no partition of relation 'article' found for row" when the default
    partition wasn't created on the target database where the API runs.
    """

    if engine.dialect.name != "postgresql":
        return

    ddl_statements = [
        # Article default partition and index
        (
            """
            CREATE TABLE IF NOT EXISTS article_default
            PARTITION OF article DEFAULT;
            """,
            """
            CREATE INDEX IF NOT EXISTS article_default_ts_pub_idx
            ON article_default (ts_pub DESC);
            """,
        ),
        # Sentiment day default partition and index
        (
            """
            CREATE TABLE IF NOT EXISTS sentiment_day_default
            PARTITION OF sentiment_day DEFAULT;
            """,
            """
            CREATE INDEX IF NOT EXISTS sentiment_day_default_dt_idx
            ON sentiment_day_default (dt DESC);
            """,
        ),
        # Prediction default partition and index
        (
            """
            CREATE TABLE IF NOT EXISTS prediction_default
            PARTITION OF prediction DEFAULT;
            """,
            """
            CREATE INDEX IF NOT EXISTS prediction_default_run_ts_idx
            ON prediction_default (run_ts DESC);
            """,
        ),
    ]

    with engine.begin() as conn:
        for create_partition, create_index in ddl_statements:
            conn.execute(text(create_partition))
            conn.execute(text(create_index))


