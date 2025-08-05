import os
from sqlalchemy import (
    create_engine, Column, String, Text, Integer, Date, DateTime, Float,
    Boolean, Numeric, JSON, Index, text
)
from sqlalchemy.orm import declarative_base, sessionmaker

from core.config import get_settings

settings = get_settings()

DATABASE_URL = settings.database_url

engine = create_engine(DATABASE_URL, future=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

Base = declarative_base()


class Article(Base):
    __tablename__ = "article"

    id = Column(String, primary_key=True)
    ticker = Column(String, nullable=False)
    headline = Column(Text)
    ts_pub = Column(DateTime)
    sentiment = Column(Integer)
    provider = Column(String)
    weight = Column(Float, default=1.0)
    raw_json = Column(JSON)

    __table_args__ = (
        Index("article_ts_idx", "ticker", "ts_pub"),
        {"postgresql_partition_by": "LIST (ticker)"},
    )


class SentimentDay(Base):
    __tablename__ = "sentiment_day"

    dt = Column(Date, primary_key=True)
    ticker = Column(String, primary_key=True)
    score = Column(Float)
    article_cnt = Column(Integer)
    explanation = Column(Text)
    is_final = Column(Boolean, default=False)

    __table_args__ = (
        Index("sentiment_day_final_idx", "ticker", "dt"),
        {"postgresql_partition_by": "LIST (ticker)"},
    )


class Prediction(Base):
    __tablename__ = "prediction"

    ticker = Column(String, primary_key=True)
    run_ts = Column(DateTime, primary_key=True)
    dt = Column(Date)
    mu = Column(Numeric(10, 2))
    sigma = Column(Numeric(10, 2))
    model_version = Column(String)
    run_type = Column(String)

    __table_args__ = (
        Index("prediction_latest_idx", "ticker", "run_ts"),
        {"postgresql_partition_by": "LIST (ticker)"},
    )


def init_db() -> None:
    """Create tables if they don't exist."""
    Base.metadata.create_all(bind=engine)

    with engine.begin() as conn:
        conn.execute(text("CREATE EXTENSION IF NOT EXISTS pg_partman"))
        conn.execute(
            text(
                "SELECT partman.create_parent('public.article', 'ticker', '1', p_type := 'list')"
            )
        )
        conn.execute(
            text(
                "SELECT partman.create_parent('public.sentiment_day', 'ticker', '1', p_type := 'list')"
            )
        )
        conn.execute(
            text(
                "SELECT partman.create_parent('public.prediction', 'ticker', '1', p_type := 'list')"
            )
        )
