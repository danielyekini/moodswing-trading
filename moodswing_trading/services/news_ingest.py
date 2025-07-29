"""Google News ingestion and sentiment classification."""

from __future__ import annotations

import asyncio
import hashlib
import math
import re
from datetime import datetime, timedelta
from typing import List
from uuid import uuid4

from dateparser import parse as parse_date

from utils.pygooglenews import GoogleNews
from models import Article
from .sentiment import SentimentService
from db import crud, models as db_models
from db.models import SessionLocal

# Publisher popularity tiers mapped to rank factors in [0.1, 1.0]
PUBLISHER_RANK = {
    "Reuters": 1.0,
    "Bloomberg": 0.9,
    "CNBC": 0.8,
}
DEFAULT_RANK = 0.5

# Recency decay constant in hours
DECAY_TAU = 6.0


class NewsIngestService:
    """Fetch articles from Google News and label sentiment."""

    def __init__(self) -> None:
        self.gn = GoogleNews()
        self.sentiment = SentimentService()

    async def collect(
        self,
        ticker: str,
        from_dt: datetime,
        to_dt: datetime,
        min_count: int = 10,
    ) -> List[Article]:
        """Collect new articles and persist them."""

        def _search(start: str, end: str):
            return self.gn.search(ticker, from_=start, to_=end)

        articles: List[Article] = []
        db_records: List[db_models.Article] = []
        look_back = 0
        cur_start = from_dt
        while len(articles) < min_count and look_back < 7:
            res = await asyncio.to_thread(
                _search, cur_start.strftime("%Y-%m-%d"), to_dt.strftime("%Y-%m-%d")
            )
            for entry in res.get("entries", []):
                title = re.sub(r"\s[-–—]\s.*", "", entry.get("title", ""))
                ts_raw = entry.get("published")
                ts = parse_date(ts_raw) or datetime.utcnow()
                source = entry.get("source", {}).get("title", "Unknown")
                sentiment = await self.sentiment.score(title)
                art_id = hashlib.sha256(entry.get("link", str(uuid4())).encode()).hexdigest()
                age_hours = max((datetime.utcnow() - ts).total_seconds() / 3600, 0.0)
                rank = PUBLISHER_RANK.get(source, DEFAULT_RANK)
                time_factor = math.exp(-age_hours / DECAY_TAU)
                weight = rank * time_factor
                articles.append(
                    Article(
                        id=art_id,
                        headline=title,
                        source=source,
                        ts_pub=ts.isoformat() + "Z",
                        sentiment=sentiment,
                    )
                )
                db_records.append(
                    db_models.Article(
                        id=art_id,
                        ticker=ticker.upper(),
                        headline=title,
                        ts_pub=ts,
                        sentiment=sentiment,
                        provider=source,
                        weight=weight,
                        raw_json=entry,
                    )
                )
            if len(articles) < min_count:
                look_back += 1
                cur_start = cur_start - timedelta(days=1)
            else:
                break

        articles = articles[:min_count]
        db_records = db_records[: len(articles)]

        if db_records:
            total_w = sum(r.weight for r in db_records)
            if total_w > 0:
                for r in db_records:
                    r.weight = r.weight / total_w
            with SessionLocal() as db:
                crud.save_articles(db, db_records)

        return articles

    async def fetch(self, ticker: str, order: str = "desc") -> List[Article]:
        """Fetch articles for ticker from the last 24h stored in DB."""

        def _query():
            start = datetime.utcnow() - timedelta(days=1)
            with SessionLocal() as db:
                q = (
                    db.query(db_models.Article)
                    .filter(db_models.Article.ticker == ticker.upper(), db_models.Article.ts_pub >= start)
                )
                if order == "asc":
                    q = q.order_by(db_models.Article.ts_pub.asc())
                else:
                    q = q.order_by(db_models.Article.ts_pub.desc())
                return q.all()

        rows = await asyncio.to_thread(_query)
        return [
            Article(
                id=r.id,
                headline=r.headline,
                source=r.provider,
                ts_pub=r.ts_pub.isoformat() + "Z",
                sentiment=r.sentiment,
            )
            for r in rows
        ]