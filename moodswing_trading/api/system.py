from fastapi import APIRouter
from services.universe import UniverseService

router = APIRouter(
    prefix="/api/v1/system",
    tags=["system"],
)

universe = UniverseService()

@router.get("/universe")
async def get_universe():
    """Return current trading universe from the database."""
    tickers = universe.list_tickers(active_only=True)
    return {"universe": [{"ticker": t} for t in tickers]}

@router.get("/notice")
async def get_notice():
    """Return legal and risk disclaimers."""
    text = (
        "This service provides market data and sentiment information for\n"
        "informational purposes only and does not constitute investment advice."
    )
    return {"notice": text}