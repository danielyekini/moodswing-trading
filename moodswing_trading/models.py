from pydantic import BaseModel
from typing import Optional, List

class ProblemDetails(BaseModel):
    type: str = "about:blank"
    title: str
    status: int
    detail: Optional[str] = None
    trace_id: Optional[str] = None

class Candle(BaseModel):
    ts: str
    open: float
    high: float
    low: float
    close: float
    volume: int

class Quote(BaseModel):
    ticker: str
    bid: float
    ask: float
    last: float
    volume: Optional[int] = None

class Tick(BaseModel):
    ts: str
    price: float
    volume: int