"""Google News ingestion and sentiment classification."""

from __future__ import annotations

import asyncio
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
import hashlib


class NewsIngestService:
    """Fetch articles from Google News and label sentiment."""

    def __init__(self) -> None:
        self.gn = GoogleNews()
        self.sentiment = SentimentService()

    async def fetch(
        self,
        ticker: str,
        from_dt: datetime,
        to_dt: datetime,
        min_count: int = 10,
    ) -> List[Article]:
        """Return a list of articles within the time range."""

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
                        raw_json=entry,
                    )
                )
            if len(articles) < min_count:
                look_back += 1
                cur_start = cur_start - timedelta(days=1)
            else:
                break

        articles = articles[:min_count]
        if db_records:
            with SessionLocal() as db:
                crud.save_articles(db, db_records)

        return articles