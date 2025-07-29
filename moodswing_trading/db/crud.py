"""Lightweight CRUD helpers for SQLAlchemy models."""
from __future__ import annotations

from datetime import date, datetime
from typing import Iterable, List, Optional

from sqlalchemy.orm import Session

from .models import SessionLocal, Article, SentimentDay, Prediction


from typing import Generator

def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# --- Article Helpers -----------------------------------------------------

def save_articles(db: Session, records: Iterable[Article]) -> None:
    for rec in records:
        db.merge(rec)
    db.commit()


# --- SentimentDay Helpers ------------------------------------------------

def upsert_sentiment_day(
    db: Session,
    dt: date,
    ticker: str,
    score: float,
    article_cnt: int,
    is_final: bool = False,
) -> SentimentDay:
    obj = (
        db.query(SentimentDay)
        .filter(SentimentDay.dt == dt, SentimentDay.ticker == ticker)
        .one_or_none()
    )
    if obj:
        obj.score = score
        obj.article_cnt = article_cnt
        obj.is_final = is_final
    else:
        obj = SentimentDay(
            dt=dt,
            ticker=ticker,
            score=score,
            article_cnt=article_cnt,
            is_final=is_final,
        )
        db.add(obj)
    db.commit()
    return obj


def get_sentiment_day(db: Session, dt: date, ticker: str) -> Optional[SentimentDay]:
    return (
        db.query(SentimentDay)
        .filter(SentimentDay.dt == dt, SentimentDay.ticker == ticker)
        .one_or_none()
    )


# --- Prediction Helpers --------------------------------------------------

def insert_prediction(
    db: Session,
    ticker: str,
    dt: date,
    mu: float,
    sigma: float,
    run_ts: Optional[datetime] = None,
    model_version: str = "",
    run_type: str = "",
) -> Prediction:
    run_ts = run_ts or datetime.utcnow()
    pred = Prediction(
        ticker=ticker,
        dt=dt,
        mu=mu,
        sigma=sigma,
        run_ts=run_ts,
        model_version=model_version,
        run_type=run_type,
    )
    db.add(pred)
    db.commit()
    return pred


def get_latest_prediction(db: Session, ticker: str, dt: date) -> Optional[Prediction]:
    return (
        db.query(Prediction)
        .filter(Prediction.ticker == ticker, Prediction.dt == dt)
        .order_by(Prediction.run_ts.desc())
        .first()
    )


def list_predictions(db: Session, ticker: str, limit: int = 10) -> List[Prediction]:
    return (
        db.query(Prediction)
        .filter(Prediction.ticker == ticker)
        .order_by(Prediction.run_ts.desc())
        .limit(limit)
        .all()
    )