from fastapi import APIRouter, Path

router = APIRouter(
    prefix="/api/v1/predict",
    tags=["predict"],
)

@router.get("/{ticker}/{date}")
async def get_prediction(
    ticker: str = Path(..., min_length=1, max_length=4, regex=r"^[A-Z]+$"),
    date: str = Path(...)
):
    """Retrieve latest (mu, sigma) for that day."""
    return {"ticker": ticker, "mu": 0.0, "sigma": 0.0, "run_ts": "2025-07-08T15:00:02Z"}

@router.get("/{ticker}")
async def list_predictions(
    ticker: str = Path(..., min_length=1, max_length=4, regex=r"^[A-Z]+$")
):
    """List last n predictions."""
    return {"ticker": ticker, "predictions": []}