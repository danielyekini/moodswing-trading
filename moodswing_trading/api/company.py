from fastapi import APIRouter, Path, HTTPException

from services.company import CompanyService
from utils import cached_json_response
from utils.cache import get_json as cache_get_json, set_json as cache_set_json

router = APIRouter(
    prefix="/api/v1/company",
    tags=["company"],
)

service = CompanyService()

@router.get("/{ticker}")
async def get_company(
    ticker: str = Path(..., min_length=1, max_length=5, regex=r"^[A-Z]+$")
):
    """Get static company profile."""
    # Redis cache: 24h TTL; service also has in-memory cache
    key = f"company:{ticker.upper()}"
    try:
        cached = await cache_get_json(key)
    except Exception:
        cached = None
    if cached:
        return cached_json_response(cached, cache_seconds=86400)
    try:
        profile = await service.fetch_profile(ticker)
    except Exception as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    try:
        await cache_set_json(key, profile.model_dump(), 24 * 3600)
    except Exception:
        pass
    return cached_json_response(profile, cache_seconds=86400)