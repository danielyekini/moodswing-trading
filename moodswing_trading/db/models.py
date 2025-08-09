import os
from sqlalchemy import (
    create_engine, Column, String, Text, Integer, Date, DateTime, Float,
    Boolean, Numeric, JSON, Index
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
    ticker = Column(String, primary_key=True)
    headline = Column(Text)
    ts_pub = Column(DateTime(timezone=True), nullable=False)
    sentiment = Column(Integer, nullable=False)
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
    score = Column(Float, nullable=False)
    article_cnt = Column(Integer, nullable=False)
    explanation = Column(Text)
    is_final = Column(Boolean, default=False)
    provisional_ts = Column(DateTime(timezone=True))

    __table_args__ = (
        Index("sentiment_day_dt_idx", "ticker", "dt"),
        {"postgresql_partition_by": "LIST (ticker)"},
    )


class Prediction(Base):
    __tablename__ = "prediction"

    ticker = Column(String, primary_key=True)
    run_ts = Column(DateTime(timezone=True), primary_key=True)
    dt = Column(Date)
    mu = Column(Numeric(10, 2), nullable=False)
    sigma = Column(Numeric(10, 2), nullable=False)
    model_version = Column(String, nullable=False)
    run_type = Column(String)

    __table_args__ = (
        Index("prediction_run_ts_idx", "ticker", "run_ts"),
        {"postgresql_partition_by": "LIST (ticker)"},
    )

