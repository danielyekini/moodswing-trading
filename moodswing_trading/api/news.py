from datetime import datetime
from fastapi import APIRouter, Path, Query

from services.news_ingest import NewsIngestService

router = APIRouter(
    prefix="/api/v1/news",
    tags=["news"],
)

service = NewsIngestService()


@router.get("/{ticker}")
async def get_news(
    ticker: str = Path(..., min_length=1, max_length=4, regex=r"^[A-Z]+$"),
    from_: str = Query(None, alias="from"),
    to: str = Query(None),
    min_count: int = Query(10),
):
    """Fetch news articles for a ticker."""
    to_dt = datetime.fromisoformat(to) if to else datetime.utcnow()
    from_dt = datetime.fromisoformat(from_) if from_ else datetime(to_dt.year, to_dt.month, to_dt.day)
    articles = await service.fetch(ticker, from_dt, to_dt, min_count)
    return {"ticker": ticker, "articles": [a.model_dump() for a in articles]}