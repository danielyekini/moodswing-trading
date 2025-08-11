from fastapi import APIRouter, Path, HTTPException
from datetime import datetime, timedelta, timezone
from services.predictor import PredictorService
from models import PredictionResult
from utils import cached_json_response
from utils.cache import get_json as cache_get_json, set_json as cache_set_json

router = APIRouter(
    prefix="/api/v1/predict",
    tags=["predict"],
)

service = PredictorService()

@router.get("/{ticker}/{date}")
async def get_prediction(
    ticker: str = Path(..., min_length=1, max_length=5, regex=r"^[A-Z]+$"),
    date: str = Path(...)
):
    """Retrieve latest (mu, sigma) for that day."""

    dt = datetime.fromisoformat(date).date()
    # Redis cache key per ticker+date
    cache_key = f"predict:{ticker.upper()}:{dt.isoformat()}"
    try:
        cached = await cache_get_json(cache_key)
    except Exception:
        cached = None
    if cached:
        # Compute TTL to next scheduled run: top of next hour (hourly) and guard with floor 60s
        now = datetime.now(timezone.utc)
        next_hour = (now.replace(minute=0, second=0, microsecond=0) + timedelta(hours=1))
        ttl = max(60, int((next_hour - now).total_seconds()))
        return cached_json_response(cached, cache_seconds=ttl)

    pred = await service.get_prediction(ticker, dt)
    if not pred:
        raise HTTPException(status_code=404, detail="not found")
    payload = pred.model_dump()
    try:
        await cache_set_json(cache_key, payload, 1800)
    except Exception:
        pass
    # Cache until the next hourly run (dynamic TTL aligned to schedule)
    now = datetime.now(timezone.utc)
    next_hour = (now.replace(minute=0, second=0, microsecond=0) + timedelta(hours=1))
    ttl = max(60, int((next_hour - now).total_seconds()))
    return cached_json_response(payload, cache_seconds=ttl)

@router.get("/{ticker}")
async def list_predictions(
    ticker: str = Path(..., min_length=1, max_length=5, regex=r"^[A-Z]+$")
):
    """List last n predictions."""

    records = await service.list_predictions(ticker)
    payload = {
        "ticker": ticker.upper(),
        "predictions": [r.model_dump() for r in records],
    }
    now = datetime.now(timezone.utc)
    next_hour = (now.replace(minute=0, second=0, microsecond=0) + timedelta(hours=1))
    ttl = max(60, int((next_hour - now).total_seconds()))
    return cached_json_response(payload, cache_seconds=ttl)