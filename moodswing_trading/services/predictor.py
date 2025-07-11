"""Prediction retrieval service."""
from __future__ import annotations

import asyncio
from datetime import date
from typing import List, Optional

from db import crud
from db.models import SessionLocal


class PredictorService:
    """Provide access to stored prediction rows."""

    async def get_prediction(self, ticker: str, dt: date):
        """Return the latest prediction for ``ticker`` on ``dt``."""

        def _fetch():
            with SessionLocal() as db:
                return crud.get_latest_prediction(db, ticker.upper(), dt)

        return await asyncio.to_thread(_fetch)

    async def list_predictions(self, ticker: str, limit: int = 10):
        """Return last ``limit`` predictions for ``ticker``."""

        def _fetch():
            with SessionLocal() as db:
                return crud.list_predictions(db, ticker.upper(), limit)

        return await asyncio.to_thread(_fetch)