from fastapi import APIRouter, Path

router = APIRouter(
    prefix="/api/v1/sentiment",
    tags=["sentiment"],
)

@router.get("/{ticker}/{date}")
async def get_sentiment(
    ticker: str = Path(..., min_length=1, max_length=4, regex=r"^[A-Z]+$"),
    date: str = Path(...)
):
    """Get rolling sentiment score for <ticker, date>."""
    return {"ticker": ticker, "date": date, "score": 0.0, "article_cnt": 0, "is_final": False}