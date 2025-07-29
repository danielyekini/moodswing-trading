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
    order: str = Query("desc"),
):
    """Fetch recent news articles for a ticker."""
    articles = await service.fetch(ticker, order)
    return {"ticker": ticker, "articles": [a.model_dump() for a in articles]}