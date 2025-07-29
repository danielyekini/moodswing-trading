from pydantic import BaseModel, ConfigDict
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

class CompanyProfile(BaseModel):
    ticker: str
    name: str
    sector: Optional[str] = None
    industry: Optional[str] = None
    exchange: Optional[str] = None

class Article(BaseModel):
    id: str
    headline: str
    source: str
    ts_pub: str
    sentiment: int

class SentimentRecord(BaseModel):
    """Aggregated sentiment score for a trading day."""

    model_config = ConfigDict(from_attributes=True)

    ticker: str
    date: str
    score: float
    article_cnt: int
    is_final: bool


class PredictionResult(BaseModel):
    """Model prediction output."""

    model_config = ConfigDict(from_attributes=True)

    ticker: str
    mu: float
    sigma: float
    run_ts: str
    model_version: str
    run_type: str