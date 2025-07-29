import os
import asyncio
from datetime import date, datetime
from typing import List, AsyncGenerator, Optional, Any, Union
import contextlib

import httpx
import yfinance as yf


class HistoryDownloadError(Exception):
    """Raised when yfinance fails to return historical data."""

    pass

from models import Candle, Quote, Tick

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
        try:
            data = await asyncio.to_thread(
                yf.download,
                ticker,
                start=start.isoformat(),
                end=end.isoformat(),
                interval=interval,
            )
        except Exception as exc:
            msg = str(exc)
            if any(term in msg for term in ("ProxyError", "ConnectionError")):
                msg += " - Unable to reach Yahoo Finance (fc.yahoo.com). Check network or proxy settings."
            raise HistoryDownloadError(msg) from exc

        if data.empty:
            raise HistoryDownloadError(f"no data returned for {ticker}")
        
        candles: List[Candle] = []
        for ts, row in data.iterrows():
            candles.append(
                Candle(
                    ts=ts.date().isoformat(),
                    open=float(row.iloc[3]),
                    high=float(row.iloc[1]),
                    low=float(row.iloc[2]),
                    close=float(row.iloc[0]),
                    volume=int(row.iloc[4]),
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

    async def tick_stream(
        self,
        ticker: str,
        interval: float = 1.0,
        ping_interval: float = 30.0,
    ) -> AsyncGenerator[Union[Tick, str], None]:
        """Yield live ticks and periodic ``"PING"`` tokens.

        When the internal queue grows beyond 500 items the oldest
        message will be dropped.
        """

        queue: asyncio.Queue[Any] = asyncio.Queue(maxsize=500)

        async def produce_ticks() -> None:
            while True:
                quote = await self.fetch_intraday_quote(ticker)
                tick = Tick(
                    ts=datetime.utcnow().isoformat() + "Z",
                    price=quote.last,
                    volume=quote.volume or 0,
                )
                if queue.full():
                    queue.get_nowait()
                queue.put_nowait(tick)
                await asyncio.sleep(interval)

        async def produce_ping() -> None:
            while True:
                if queue.full():
                    queue.get_nowait()
                queue.put_nowait("PING")
                await asyncio.sleep(ping_interval)

        tick_task = asyncio.create_task(produce_ticks())
        ping_task = asyncio.create_task(produce_ping())
        try:
            while True:
                msg = await queue.get()
                yield msg
        finally:
            tick_task.cancel()
            ping_task.cancel()
            for task in (tick_task, ping_task):
                with contextlib.suppress(asyncio.CancelledError):
                    await task