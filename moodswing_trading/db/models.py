import os
from sqlalchemy import (
    create_engine, Column, String, Text, Integer, Date, DateTime, Float,
    Boolean, Numeric, JSON, Index
)
from sqlalchemy.orm import declarative_base, sessionmaker

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./moodswing.db")

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
    raw_json = Column(JSON)

    __table_args__ = (
        Index("article_ts_idx", "ticker", "ts_pub"),
    )


class SentimentDay(Base):
    __tablename__ = "sentiment_day"

    dt = Column(Date, primary_key=True)
    ticker = Column(String, primary_key=True)
    score = Column(Float)
    article_cnt = Column(Integer)
    is_final = Column(Boolean, default=False)

    __table_args__ = (
        Index("sentiment_day_final_idx", "ticker", "dt"),
    )


class Prediction(Base):
    __tablename__ = "prediction"

    ticker = Column(String, primary_key=True)
    run_ts = Column(DateTime, primary_key=True)
    dt = Column(Date)
    mu = Column(Numeric(10, 2))
    sigma = Column(Numeric(10, 2))

    __table_args__ = (
        Index("prediction_latest_idx", "ticker", "run_ts"),
    )


def init_db() -> None:
    """Create tables if they don't exist."""
    Base.metadata.create_all(bind=engine)