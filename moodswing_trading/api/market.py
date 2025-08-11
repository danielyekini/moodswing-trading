from datetime import date
from fastapi import APIRouter, WebSocket, Path, Query, HTTPException
import asyncio

from services.market import MarketService, HistoryDownloadError
from utils import cached_json_response
from models import Candle, Quote, Tick
from utils.cache import get_json as cache_get_json, set_json as cache_set_json
from core.ws_ratelimit import WsRateLimiter

router = APIRouter(
    prefix="/api/v1/stocks",
    tags=["market"],
)

service = MarketService()

@router.get("/{ticker}/history", response_model=dict)
async def get_history(
    ticker: str = Path(..., min_length=1, max_length=5, regex=r"^[A-Z]+$"),
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
    payload = {
        "ticker": ticker,
        "interval": interval,
        "candles": [c.model_dump() for c in candles],
    }
    return cached_json_response(payload, cache_seconds=300)

@router.get("/{ticker}/intraday", response_model=Quote)
async def get_intraday(
    ticker: str = Path(..., min_length=1, max_length=5, regex=r"^[A-Z]+$")
):
    """Latest quote snapshot (bid, ask, last)."""
    # Redis cache: quotes 10s TTL
    key = f"quote:{ticker.upper()}"
    try:
        cached = await cache_get_json(key)
    except Exception:
        cached = None
    if cached:
        return Quote(**cached)
    quote = await service.fetch_intraday_quote(ticker)
    try:
        await cache_set_json(key, quote.model_dump(), 10)
    except Exception:
        pass
    return quote

@router.websocket("/{ticker}/stream")
async def stream_ticks(websocket: WebSocket, ticker: str):
    """Real-time tick push (JSON frames)."""
    await websocket.accept()
    try:
        # Allow client to pass interval in query string, default to 5s
        try:
            qs = dict([part.split("=", 1) for part in (websocket.url.query or "").split("&") if part])
            interval = float(qs.get("interval", 5.0))
            interval = max(1.0, min(interval, 60.0))
        except Exception:
            interval = 5.0

        # Per-connection soft rate meter
        rlm = WsRateLimiter(limit=60, window_seconds=60)
        snap = rlm.snapshot()
        await websocket.send_json({"type": "rate", "limit": snap.limit, "remaining": snap.remaining, "reset": snap.reset_seconds})

        async for msg in service.tick_stream(ticker, interval=interval):
            # Emit rate info before each tick
            state = rlm.tick()
            await websocket.send_json({"type": "rate", "limit": state.limit, "remaining": state.remaining, "reset": state.reset_seconds})
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


