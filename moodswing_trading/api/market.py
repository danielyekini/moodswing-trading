from datetime import date
from fastapi import APIRouter, WebSocket, Path, Query, HTTPException
import asyncio

from services.market import MarketService, HistoryDownloadError
from models import Candle, Quote, Tick

router = APIRouter(
    prefix="/api/v1/stocks",
    tags=["market"],
)

service = MarketService()

@router.get("/{ticker}/history", response_model=dict)
async def get_history(
    ticker: str = Path(..., min_length=1, max_length=4, regex=r"^[A-Z]+$"),
    start: date = Query(...),
    end: date = Query(None),
    interval: str = Query("1d", regex=r"^(1d|1wk|1mo)$"),
):
    """Fetch OHLCV candles for a given resolution."""
    if end is None:
        end = date.today()
    if start > end:
        raise HTTPException(status_code=400, detail="invalid date range")
    try:
        candles = await service.fetch_history(ticker, start, end, interval)
    except HistoryDownloadError as exc:
        raise HTTPException(status_code=503, detail=str(exc))
    return {"ticker": ticker, "interval": interval, "candles": [c.model_dump() for c in candles]}

@router.get("/{ticker}/intraday", response_model=Quote)
async def get_intraday(
    ticker: str = Path(..., min_length=1, max_length=4, regex=r"^[A-Z]+$")
):
    """Latest quote snapshot (bid, ask, last)."""
    return await service.fetch_intraday_quote(ticker)

@router.websocket("/{ticker}/stream")
async def stream_ticks(websocket: WebSocket, ticker: str):
    """Real-time tick push (JSON frames)."""
    await websocket.accept()
    try:
        async for msg in service.tick_stream(ticker):
            if isinstance(msg, str) and msg == "PING":
                await websocket.send_json({"type": "ping"})
                try:
                    reply = await asyncio.wait_for(websocket.receive_json(), timeout=10)
                except asyncio.TimeoutError:
                    break
                if not isinstance(reply, dict) or reply.get("type") != "pong":
                    break
                continue
            await websocket.send_json(msg.dict())
    finally:
        await websocket.close()


