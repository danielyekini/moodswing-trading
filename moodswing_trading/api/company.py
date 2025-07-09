from fastapi import APIRouter, Path

router = APIRouter(
    prefix="/api/v1/company",
    tags=["company"],
)

@router.get("/{ticker}")
async def get_company(
    ticker: str = Path(..., min_length=1, max_length=4, regex=r"^[A-Z]+$")
):
    """Get static company profile."""
    return {
        "ticker": ticker,
        "name": "Example Corp",
        "sector": "Technology",
        "industry": "Software—Infrastructure",
        "exchange": "NASDAQ"
    } 