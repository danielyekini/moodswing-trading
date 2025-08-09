from fastapi import APIRouter, Path, Query
from datetime import datetime

from services.news_ingest import NewsIngestService
from utils import cached_json_response

router = APIRouter(
    prefix="/api/v1/news",
    tags=["news"],
)

service = NewsIngestService()

@router.get("/{ticker}/collect")
async def collect_news(
    ticker: str = Path(..., min_length=1, max_length=4, regex=r"^[A-Z]+$"),
    from_: str = Query(None, alias="from"),
    to: str = Query(None),
    min_count: int = Query(10),
) -> str:
    """Collect and persist news articles for a ticker."""
    to_dt = datetime.fromisoformat(to) if to else datetime.utcnow()
    from_dt = datetime.fromisoformat(from_) if from_ else datetime(to_dt.year, to_dt.month, to_dt.day)
    articles = await service.collect(ticker, from_dt, to_dt, min_count)
    # try:
    #     articles = await service.collect(ticker, from_dt, to_dt, min_count)
    # except Exception as exc:
    #     raise Exception(status_code=404, detail=str(exc)) from exc
    
    if not articles:
        return "Failed"
    
    return "Success"

@router.get("/{ticker}")
async def fetch_news(
    ticker: str = Path(..., min_length=1, max_length=4, regex=r"^[A-Z]+$"),
    order: str = Query("desc"),
    limit: int = Query(50, gt=0, le=100),
    cursor: str | None = Query(None),
):
    """Fetch recent news articles for a ticker with cursor based pagination."""
    articles, next_cur, prev_cur = await service.fetch(
        ticker, order=order, limit=limit, cursor=cursor
    )
    payload = {
        "ticker": ticker,
        "articles": [a.model_dump() for a in articles],
        "next_cursor": next_cur,
        "prev_cursor": prev_cur,
    }
    return cached_json_response(payload, cache_seconds=300)