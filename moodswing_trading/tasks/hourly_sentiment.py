"""Aggregate article sentiment into daily rolling scores."""

from __future__ import annotations

import json
import os
from datetime import datetime, timedelta

import redis

from moodswing_trading.core.celery_app import celery_app
from db import crud, models as db_models
from db.models import SessionLocal


REDIS = redis.Redis.from_url(os.getenv("REDIS_URL", "redis://localhost:6379/0"))
TICKERS = [t.strip().upper() for t in os.getenv("TICKERS", "").split(",") if t.strip()]


@celery_app.task(name="hourly_sentiment_refresh")
def refresh() -> None:
    """Update rolling sentiment scores and publish."""

    today = datetime.utcnow().date()
    start = datetime.combine(today, datetime.min.time())
    end = start + timedelta(days=1)

    with SessionLocal() as db:
        for ticker in TICKERS:
            rows = (
                db.query(db_models.Article)
                .filter(
                    db_models.Article.ticker == ticker,
                    db_models.Article.ts_pub >= start,
                    db_models.Article.ts_pub < end,
                )
                .all()
            )
            if not rows:
                continue
            score = sum(r.sentiment for r in rows) / len(rows)
            rec = crud.upsert_sentiment_day(
                db, today, ticker, score, len(rows), is_final=False
            )
            payload = {
                "ticker": ticker,
                "date": today.isoformat(),
                "score": rec.score,
                "article_cnt": rec.article_cnt,
                "is_final": rec.is_final,
            }
            REDIS.publish("sentiment_day", json.dumps(payload))