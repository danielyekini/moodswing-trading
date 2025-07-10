from fastapi import APIRouter, Path, HTTPException

from services.company import CompanyService

router = APIRouter(
    prefix="/api/v1/company",
    tags=["company"],
)

service = CompanyService()

@router.get("/{ticker}")
async def get_company(
    ticker: str = Path(..., min_length=1, max_length=4, regex=r"^[A-Z]+$")
):
    """Get static company profile."""
    try:
        return await service.fetch_profile(ticker)
    except Exception as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc