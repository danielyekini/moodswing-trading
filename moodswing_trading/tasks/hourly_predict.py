"""Generate price forecasts and persist results."""

from __future__ import annotations

import asyncio
import json
from datetime import datetime, timedelta

import redis

from moodswing_trading.core.celery_app import celery_app
from moodswing_trading.core.config import get_settings
from moodswing_trading.core.logging import setup_logging
from db import crud
from db.models import SessionLocal
from services.market import MarketService

setup_logging()
settings = get_settings()

REDIS = redis.Redis.from_url(settings.redis_url)
TICKERS = settings.tickers

market = MarketService()


async def _predict(ticker: str) -> tuple[float, float]:
    today = datetime.utcnow().date()
    candles = await market.fetch_history(ticker, today - timedelta(days=5), today)
    if candles:
        close = candles[-1].close
    else:
        close = 0.0
    mu = close
    sigma = close * 0.02 if close else 1.0
    return mu, sigma


@celery_app.task(name="hourly_predict")
def run() -> None:
    """Run prediction model and broadcast results."""

    dt = datetime.utcnow().date()
    for ticker in TICKERS:
        mu, sigma = asyncio.run(_predict(ticker))
        with SessionLocal() as db:
            rec = crud.insert_prediction(db, ticker, dt, mu, sigma)
        payload = {
            "ticker": ticker,
            "mu": float(mu),
            "sigma": float(sigma),
            "run_ts": rec.run_ts.isoformat() + "Z",
        }
        REDIS.publish("prediction", json.dumps(payload))