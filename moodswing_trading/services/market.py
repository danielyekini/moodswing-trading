import os
import asyncio
from datetime import date, datetime
from typing import List, AsyncGenerator, Optional

import httpx
import yfinance as yf

from moodswing_trading.models import Candle, Quote, Tick

ALPHAVANTAGE_URL = "https://www.alphavantage.co/query"

class MarketService:
    """Provides historical data and live price streaming."""

    def __init__(self, api_key: Optional[str] = None) -> None:
        self.api_key = api_key or os.getenv("ALPHAVANTAGE_API_KEY", "")

    async def fetch_history(
        self,
        ticker: str,
        start: date,
        end: date,
        interval: str = "1d",
    ) -> List[Candle]:
        """Download historical candles using yfinance."""
        data = yf.download(ticker, start=start.isoformat(), end=end.isoformat(), interval=interval)
        candles: List[Candle] = []
        for ts, row in data.iterrows():
            candles.append(
                Candle(
                    ts=ts.date().isoformat(),
                    open=float(row["Open"]),
                    high=float(row["High"]),
                    low=float(row["Low"]),
                    close=float(row["Close"]),
                    volume=int(row["Volume"]),
                )
            )
        return candles

    async def fetch_intraday_quote(self, ticker: str) -> Quote:
        """Fetch the latest quote snapshot from Alpha Vantage."""
        params = {
            "function": "GLOBAL_QUOTE",
            "symbol": ticker,
            "apikey": self.api_key,
        }
        async with httpx.AsyncClient() as client:
            resp = await client.get(ALPHAVANTAGE_URL, params=params, timeout=10)
            resp.raise_for_status()
            data = resp.json().get("Global Quote", {})
        price = float(data.get("05. price", 0))
        volume = int(data.get("06. volume", 0))
        return Quote(ticker=ticker, bid=price, ask=price, last=price, volume=volume)

    async def tick_stream(self, ticker: str, interval: float = 1.0) -> AsyncGenerator[Tick, None]:
        """Yield live ticks using Alpha Vantage GLOBAL_QUOTE."""
        while True:
            quote = await self.fetch_intraday_quote(ticker)
            yield Tick(ts=datetime.utcnow().isoformat() + "Z", price=quote.last, volume=quote.volume or 0)
            await asyncio.sleep(interval)
