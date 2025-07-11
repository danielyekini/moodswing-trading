"""Sentiment classification service using transformers pipeline."""

from __future__ import annotations

import asyncio
from transformers import pipeline
from datetime import date
from db import crud
from db.models import SessionLocal


class SentimentService:
    """Wraps a text-classification model returning -1, 0, 1 scores."""

    def __init__(self, model_name: str = "nickmuchi/deberta-v3-base-finetuned-finance-text-classification") -> None:
        self._pipeline = pipeline("text-classification", model=model_name)

    async def score(self, text: str) -> int:
        """Return sentiment score for ``text`` (-1 bearish, 0 neutral, 1 bullish)."""

        def _predict() -> int:
            result = self._pipeline(text)[0]
            label = result.get("label", "").lower()
            if label == "bullish":
                return 1
            if label == "bearish":
                return -1
            return 0

        return await asyncio.to_thread(_predict)

    async def get_day_score(self, ticker: str, dt: date):
        """Fetch sentiment record for the given ticker and date from the DB."""

        def _query():
            with SessionLocal() as db:
                return crud.get_sentiment_day(db, dt, ticker.upper())

        return await asyncio.to_thread(_query)