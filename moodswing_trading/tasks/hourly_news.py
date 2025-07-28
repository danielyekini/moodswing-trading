"""Hourly ingestion of Google News articles."""

from __future__ import annotations

import asyncio
import json

from datetime import datetime, timedelta

import redis

from moodswing_trading.core.celery_app import celery_app
from moodswing_trading.core.config import get_settings
from moodswing_trading.core.logging import setup_logging
from services.news_ingest import NewsIngestService


setup_logging()
settings = get_settings()

REDIS = redis.Redis.from_url(settings.redis_url)
TICKERS = settings.tickers

news_service = NewsIngestService()


@celery_app.task(name="hourly_news_ingest")
def ingest() -> None:
    """Fetch last hour of articles and store/publish."""

    to_dt = datetime.utcnow()
    from_dt = to_dt - timedelta(hours=1)

    for ticker in TICKERS:
        articles = asyncio.run(news_service.fetch(ticker, from_dt, to_dt, 1))
        if not articles:
            continue
        payload = {
            "ticker": ticker,
            "articles": [a.model_dump() for a in articles],
        }
        REDIS.publish("news_raw", json.dumps(payload))