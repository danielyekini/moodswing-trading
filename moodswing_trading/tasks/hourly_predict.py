"""Generate price forecasts and persist results.

This task is used for both regular hourly predictions and the final
end-of-day (EOD) run. The ``run_type`` argument determines which label is
stored alongside each record.
"""

from __future__ import annotations

import asyncio
import json
from datetime import datetime, timedelta
import subprocess
from pathlib import Path

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
def run(run_type: str = "HOURLY") -> None:
    """Run prediction model and broadcast results.

    Parameters
    ----------
    run_type:
        Label applied to each prediction record. ``"HOURLY"`` for regular
        intraday runs and ``"EOD"`` for the final end-of-day prediction.
    """

    dt = datetime.utcnow().date()
    repo_root = Path(__file__).resolve().parents[1]
    try:
        git_sha = subprocess.check_output([
            "git",
            "rev-parse",
            "--short",
            "HEAD",
        ], cwd=repo_root).decode().strip()
    except Exception:
        git_sha = "unknown"
    model_version = f"{dt.isoformat()}-{git_sha}"
    for ticker in TICKERS:
        mu, sigma = asyncio.run(_predict(ticker))
        with SessionLocal() as db:
            existing = crud.get_latest_prediction(db, ticker, dt)
            if existing and existing.run_type == "EOD" and run_type == "HOURLY":
                continue
            rec = crud.upsert_prediction(
                db,
                ticker,
                dt,
                mu,
                sigma,
                model_version=model_version,
                run_type=run_type,
            )
        payload = {
            "ticker": ticker,
            "mu": float(mu),
            "sigma": float(sigma),
            "run_ts": rec.run_ts.isoformat() + "Z",
            "model_version": rec.model_version,
            "run_type": rec.run_type,
        }
        REDIS.publish("prediction", json.dumps(payload))