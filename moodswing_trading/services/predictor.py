"""Prediction retrieval service."""
from __future__ import annotations

import asyncio
from datetime import date
from typing import List, Optional

from models import PredictionResult

from db import crud
from db.models import SessionLocal


class PredictorService:
    """Provide access to stored prediction rows."""

    async def get_prediction(self, ticker: str, dt: date) -> Optional[PredictionResult]:
        """Return the latest prediction for ``ticker`` on ``dt``."""

        def _fetch():
            with SessionLocal() as db:
                return crud.get_latest_prediction(db, ticker.upper(), dt)

        rec = await asyncio.to_thread(_fetch)
        if not rec:
            return None
        return PredictionResult(
            ticker=rec.ticker,
            mu=float(rec.mu),
            sigma=float(rec.sigma),
            run_ts=rec.run_ts.isoformat() + "Z",
            model_version=rec.model_version,
            run_type=rec.run_type,
        )

    async def list_predictions(self, ticker: str, limit: int = 10) -> List[PredictionResult]:
        """Return last ``limit`` predictions for ``ticker``."""

        def _fetch():
            with SessionLocal() as db:
                return crud.list_predictions(db, ticker.upper(), limit)

        records = await asyncio.to_thread(_fetch)
        results: List[PredictionResult] = []
        for r in records:
            results.append(
                PredictionResult(
                    ticker=r.ticker,
                    mu=float(r.mu),
                    sigma=float(r.sigma),
                    run_ts=r.run_ts.isoformat() + "Z",
                    model_version=r.model_version,
                    run_type=r.run_type,
                )
            )
        return results