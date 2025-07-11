from fastapi import APIRouter, Path, HTTPException
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
    )