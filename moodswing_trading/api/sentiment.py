from fastapi import APIRouter, Path, HTTPException, WebSocket
import asyncio
from datetime import datetime
from services.sentiment import SentimentService
from models import SentimentRecord
from utils.cache import get_json as cache_get_json, set_json as cache_set_json
from core.ws_ratelimit import WsRateLimiter

router = APIRouter(
    prefix="/api/v1/sentiment",
    tags=["sentiment"],
)

service = SentimentService()

@router.get("/{ticker}/{date}")
async def get_sentiment(
    ticker: str = Path(..., min_length=1, max_length=5, regex=r"^[A-Z]+$"),
    date: str = Path(...)
):
    """Get rolling sentiment score for <ticker, date>."""

    dt = datetime.fromisoformat(date).date()
    # Redis cache per ticker+date; TTL 1h as a reasonable default for day records
    cache_key = f"sentiment:{ticker.upper()}:{dt.isoformat()}"
    cached = await cache_get_json(cache_key)
    if cached:
        return cached
    record = await service.get_day_score(ticker, dt)
    if not record:
        raise HTTPException(status_code=404, detail="not found")
    payload = SentimentRecord(
        ticker=ticker.upper(),
        date=date,
        score=record.score,
        article_cnt=record.article_cnt,
        is_final=record.is_final,
        explanation=record.explanation,
    )
    try:
        await cache_set_json(cache_key, payload.model_dump(), 3600)
    except Exception:
        pass
    return payload

@router.get("/{ticker}/latest")
async def get_latest_sentiment(
    ticker: str = Path(..., min_length=1, max_length=5, regex=r"^[A-Z]+$")
):
    cache_key = f"sentiment:{ticker.upper()}:latest"
    cached = await cache_get_json(cache_key)
    if cached:
        return cached
    rec = await service.get_latest(ticker)
    if not rec:
        raise HTTPException(status_code=404, detail="not found")
    payload = SentimentRecord(
        ticker=ticker.upper(),
        date=rec.dt.isoformat(),
        score=rec.score,
        article_cnt=rec.article_cnt,
        is_final=rec.is_final,
        explanation=rec.explanation,
    )
    try:
        await cache_set_json(cache_key, payload.model_dump(), 3600)
    except Exception:
        pass
    return payload

@router.websocket("/stream")
async def stream_updates(websocket: WebSocket):
    """Push sentiment day updates in real-time."""
    await websocket.accept()
    try:
        # Per-connection rate meter
        rlm = WsRateLimiter(limit=60, window_seconds=60)
        snap = rlm.snapshot()
        await websocket.send_json({"type": "rate", "limit": snap.limit, "remaining": snap.remaining, "reset": snap.reset_seconds})
        async for msg in service.update_stream():
            # Emit rate info before each message
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
            await websocket.send_json(msg)
    finally:
        await websocket.close()