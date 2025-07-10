"""Company profile fetch and simple in-memory cache."""

from __future__ import annotations

import asyncio
from datetime import datetime, timedelta
from typing import Dict, Tuple

import yfinance as yf

from models import CompanyProfile


class CompanyService:
    """Fetch company metadata from yfinance with basic caching."""

    def __init__(self, ttl_hours: int = 24) -> None:
        self.ttl = timedelta(hours=ttl_hours)
        self._cache: Dict[str, Tuple[CompanyProfile, datetime]] = {}

    async def fetch_profile(self, ticker: str) -> CompanyProfile:
        """Return company profile for ``ticker``.

        Data is cached in memory for ``ttl_hours`` to avoid repeated API calls.
        """

        ticker = ticker.upper()
        now = datetime.utcnow()
        cached = self._cache.get(ticker)
        if cached and now - cached[1] < self.ttl:
            return cached[0]

        def _load() -> CompanyProfile:
            info = yf.Ticker(ticker).info or {}
            return CompanyProfile(
                ticker=ticker,
                name=info.get("longName") or info.get("shortName") or ticker,
                sector=info.get("sector"),
                industry=info.get("industry"),
                exchange=info.get("exchange"),
            )

        profile = await asyncio.to_thread(_load)
        self._cache[ticker] = (profile, now)
        return profile