from __future__ import annotations

from datetime import datetime, timezone
from typing import List

from db.models import SessionLocal, TickerUniverse


class UniverseService:
    """Ticker universe registry backed by the database."""

    def add_ticker(self, ticker: str, active: bool = True) -> None:
        ticker_upper = ticker.upper()
        with SessionLocal() as db:
            existing = (
                db.query(TickerUniverse)
                .filter(TickerUniverse.ticker == ticker_upper)
                .one_or_none()
            )
            if existing:
                if existing.active != active:
                    existing.active = active
                    db.commit()
                return
            db.add(
                TickerUniverse(
                    ticker=ticker_upper,
                    active=active,
                    added_at=datetime.now(timezone.utc),
                )
            )
            db.commit()

    def list_tickers(self, active_only: bool = True) -> List[str]:
        with SessionLocal() as db:
            query = db.query(TickerUniverse.ticker)
            if active_only:
                query = query.filter(TickerUniverse.active.is_(True))
            return [row[0] for row in query.all()]



