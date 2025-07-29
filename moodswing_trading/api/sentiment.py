from fastapi import APIRouter, Path, HTTPException, WebSocket
import asyncio
from datetime import datetime
from services.sentiment import SentimentService
from models import SentimentRecord

router = APIRouter(
    prefix="/api/v1/sentiment",
    tags=["sentiment"],
)

service = SentimentService()

@router.get("/{ticker}/{date}")
async def get_sentiment(
    ticker: str = Path(..., min_length=1, max_length=4, regex=r"^[A-Z]+$"),
    date: str = Path(...)
):
    """Get rolling sentiment score for <ticker, date>."""

    dt = datetime.fromisoformat(date).date()
    record = await service.get_day_score(ticker, dt)
    if not record:
        raise HTTPException(status_code=404, detail="not found")
    return SentimentRecord(
        ticker=ticker.upper(),
        date=date,
        score=record.score,
        article_cnt=record.article_cnt,
        is_final=record.is_final,
        explanation=record.explanation,
    )

@router.websocket("/stream")
async def stream_updates(websocket: WebSocket):
    """Push sentiment day updates in real-time."""
    await websocket.accept()
    try:
        async for msg in service.update_stream():
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