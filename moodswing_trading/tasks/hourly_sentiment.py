"""Aggregate article sentiment into daily rolling scores."""

from __future__ import annotations

import json
from datetime import datetime, timedelta

import redis

from moodswing_trading.core.celery_app import celery_app
from moodswing_trading.core.config import get_settings
from moodswing_trading.core.logging import setup_logging
from db import crud, models as db_models
from db.models import SessionLocal

def _summarize(headlines: list[str]) -> str:
    """Return a short summary of headlines (placeholder for LLM)."""
    text = "; ".join(headlines)
    return text[:120]

setup_logging()
settings = get_settings()

REDIS = redis.Redis.from_url(settings.redis_url)
TICKERS = settings.tickers

@celery_app.task(name="hourly_sentiment_refresh")
def refresh() -> None:
    """Update rolling sentiment scores and publish."""

    now = datetime.utcnow()
    is_final = now.hour == 0
    target_date = now.date() - timedelta(days=1) if is_final else now.date()
    start = datetime.combine(target_date, datetime.min.time())
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
            total_weight = sum(r.weight or 1.0 for r in rows)
            if total_weight == 0:
                continue
            raw = sum((r.sentiment * (r.weight or 1.0)) for r in rows) / total_weight
            score = round((raw + 1) * 50, 1)
            top_rows = sorted(rows, key=lambda r: r.weight or 1.0, reverse=True)[:3]
            explanation = _summarize([r.headline for r in top_rows])
            rec = crud.upsert_sentiment_day(
                db,
                target_date,
                ticker,
                score,
                len(rows),
                explanation=explanation,
                is_final=is_final,
            )
            payload = {
                "ticker": ticker,
                "date": target_date.isoformat(),
                "score": rec.score,
                "article_cnt": rec.article_cnt,
                "is_final": rec.is_final,
                "explanation": rec.explanation,
            }
            REDIS.publish("sentiment_day", json.dumps(payload))