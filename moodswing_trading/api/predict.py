from fastapi import APIRouter, Path, HTTPException
from datetime import datetime
from services.predictor import PredictorService
from models import PredictionResult

router = APIRouter(
    prefix="/api/v1/predict",
    tags=["predict"],
)

service = PredictorService()

@router.get("/{ticker}/{date}")
async def get_prediction(
    ticker: str = Path(..., min_length=1, max_length=4, regex=r"^[A-Z]+$"),
    date: str = Path(...)
):
    """Retrieve latest (mu, sigma) for that day."""

    dt = datetime.fromisoformat(date).date()
    pred = await service.get_prediction(ticker, dt)
    if not pred:
        raise HTTPException(status_code=404, detail="not found")
    return pred

@router.get("/{ticker}")
async def list_predictions(
    ticker: str = Path(..., min_length=1, max_length=4, regex=r"^[A-Z]+$")
):
    """List last n predictions."""

    records = await service.list_predictions(ticker)
    return {
        "ticker": ticker.upper(),
        "predictions": [r.model_dump() for r in records],
    }