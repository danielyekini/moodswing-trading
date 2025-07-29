"""Sentiment classification service using transformers pipeline."""

from __future__ import annotations

import asyncio
from transformers import pipeline
from datetime import date
from typing import AsyncGenerator, Any, Union
import contextlib
import json
import redis.asyncio as redis

from db import crud
from db.models import SessionLocal
from core.config import get_settings


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
    
    async def update_stream(
        self,
        ping_interval: float = 30.0,
    ) -> AsyncGenerator[Union[dict, str], None]:
        """Yield sentiment day updates from Redis and periodic ``"PING"`` tokens."""

        settings = get_settings()
        client = redis.from_url(settings.redis_url)
        pubsub = client.pubsub()
        await pubsub.subscribe("sentiment_day")

        queue: asyncio.Queue[Any] = asyncio.Queue(maxsize=500)

        async def read_messages() -> None:
            async for msg in pubsub.listen():
                if msg.get("type") != "message":
                    continue
                data = msg.get("data")
                if queue.full():
                    queue.get_nowait()
                queue.put_nowait(data)

        async def produce_ping() -> None:
            while True:
                if queue.full():
                    queue.get_nowait()
                queue.put_nowait("PING")
                await asyncio.sleep(ping_interval)

        reader_task = asyncio.create_task(read_messages())
        ping_task = asyncio.create_task(produce_ping())
        try:
            while True:
                msg = await queue.get()
                if msg == "PING":
                    yield "PING"
                    continue
                if isinstance(msg, (bytes, bytearray)):
                    msg = msg.decode()
                yield json.loads(msg)
        finally:
            reader_task.cancel()
            ping_task.cancel()
            for task in (reader_task, ping_task):
                with contextlib.suppress(asyncio.CancelledError):
                    await task
            await pubsub.unsubscribe("sentiment_day")
            await pubsub.close()
            await client.close()