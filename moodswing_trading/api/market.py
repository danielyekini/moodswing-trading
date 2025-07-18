from datetime import date
from fastapi import APIRouter, WebSocket, Path, Query, HTTPException

from services.market import MarketService
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
    candles = await service.fetch_history(ticker, start, end, interval)
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
        async for tick in service.tick_stream(ticker):
            await websocket.send_json(tick.dict())
    except Exception:
        await websocket.close()


