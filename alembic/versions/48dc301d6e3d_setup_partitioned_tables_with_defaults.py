"""setup partitioned tables with defaults

Revision ID: 48dc301d6e3d
Revises: 
Create Date: 2024-01-01

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '48dc301d6e3d'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Ensure native Postgres partitioned parents exist (no pg_partman dependency).

    op.execute(
        """
        CREATE TABLE IF NOT EXISTS article (
            id TEXT,
            ticker TEXT NOT NULL,
            headline TEXT,
            ts_pub TIMESTAMPTZ NOT NULL,
            sentiment SMALLINT NOT NULL,
            provider TEXT,
            url TEXT,
            weight REAL,
            raw_json JSONB,
            PRIMARY KEY (id, ticker)
        ) PARTITION BY LIST (ticker);
        """
    )
    op.execute(
        "CREATE TABLE IF NOT EXISTS article_default PARTITION OF article DEFAULT;"
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS article_default_ts_pub_idx ON article_default (ts_pub DESC);"
    )

    op.execute(
        """
        CREATE TABLE IF NOT EXISTS sentiment_day (
            dt DATE NOT NULL,
            ticker TEXT NOT NULL,
            score REAL NOT NULL,
            article_cnt INT NOT NULL,
            explanation TEXT,
            is_final BOOL DEFAULT FALSE,
            provisional_ts TIMESTAMPTZ,
            PRIMARY KEY (dt, ticker)
        ) PARTITION BY LIST (ticker);
        """
    )
    op.execute(
        "CREATE TABLE IF NOT EXISTS sentiment_day_default PARTITION OF sentiment_day DEFAULT;"
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS sentiment_day_default_dt_idx ON sentiment_day_default (dt DESC);"
    )

    op.execute(
        """
        CREATE TABLE IF NOT EXISTS prediction (
            ticker TEXT NOT NULL,
            run_ts TIMESTAMPTZ NOT NULL,
            dt DATE,
            mu NUMERIC(10,2) NOT NULL,
            sigma NUMERIC(10,2) NOT NULL,
            model_version TEXT NOT NULL,
            run_type TEXT,
            PRIMARY KEY (ticker, run_ts)
        ) PARTITION BY LIST (ticker);
        """
    )
    op.execute(
        "CREATE TABLE IF NOT EXISTS prediction_default PARTITION OF prediction DEFAULT;"
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS prediction_default_run_ts_idx ON prediction_default (run_ts DESC);"
    )


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS prediction CASCADE;")
    op.execute("DROP TABLE IF EXISTS sentiment_day CASCADE;")
    op.execute("DROP TABLE IF EXISTS article CASCADE;")

    op.create_table(
        'article',
        sa.Column('id', sa.Text(), primary_key=True),
        sa.Column('ticker', sa.Text(), nullable=False),
        sa.Column('headline', sa.Text()),
        sa.Column('ts_pub', sa.DateTime(timezone=True), nullable=False),
        sa.Column('sentiment', sa.SmallInteger(), nullable=False),
        sa.Column('provider', sa.Text()),
        sa.Column('weight', sa.Float()),
        sa.Column('raw_json', sa.JSON()),
    )
    op.create_table(
        'sentiment_day',
        sa.Column('dt', sa.Date(), primary_key=True),
        sa.Column('ticker', sa.Text(), primary_key=True),
        sa.Column('score', sa.Float(), nullable=False),
        sa.Column('article_cnt', sa.Integer(), nullable=False),
        sa.Column('explanation', sa.Text()),
        sa.Column('is_final', sa.Boolean(), nullable=False, server_default=sa.text('false')),
        sa.Column('provisional_ts', sa.DateTime(timezone=True)),
    )
    op.create_table(
        'prediction',
        sa.Column('ticker', sa.Text(), primary_key=True),
        sa.Column('run_ts', sa.DateTime(timezone=True), primary_key=True),
        sa.Column('dt', sa.Date()),
        sa.Column('mu', sa.Numeric(10,2), nullable=False),
        sa.Column('sigma', sa.Numeric(10,2), nullable=False),
        sa.Column('model_version', sa.Text(), nullable=False),
        sa.Column('run_type', sa.Text()),
    )