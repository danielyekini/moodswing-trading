from fastapi import APIRouter
from core.config import get_settings

router = APIRouter(
    prefix="/api/v1/system",
    tags=["system"],
)

settings = get_settings()

@router.get("/universe")
async def get_universe():
    """Return configured trading universe."""
    universe = [
        {
            "ticker": t,
            "name": f"{t} Inc.",
            "sector": "Unknown",
            "listed_since": None,
        }
        for t in settings.tickers
    ]
    return {"universe": universe}