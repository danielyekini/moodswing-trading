from fastapi import APIRouter, Path, Query

router = APIRouter(
    prefix="/api/v1/news",
    tags=["news"],
)

@router.get("/{ticker}")
async def get_news(
    ticker: str = Path(..., min_length=1, max_length=4, regex=r"^[A-Z]+$"),
    from_: str = Query(None, alias="from"),
    to: str = Query(None),
    min_count: int = Query(10)
):
    """Fetch news articles for a ticker."""
    return {"ticker": ticker, "articles": []}


# /news/latest