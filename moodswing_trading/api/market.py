from fastapi import APIRouter, WebSocket, Path, Query

router = APIRouter(
    prefix="/api/v1/stocks",
    tags=["market"],
)

@router.get("/{ticker}/history")
async def get_history(
    ticker: str = Path(..., min_length=1, max_length=4, regex=r"^[A-Z]+$"),
    start: str = Query(...),
    end: str = Query(None),
    interval: str = Query("1d", regex=r"^(1d|1wk|1mo)$")
):
    """Fetch OHLCV candles for a given resolution."""
    return {"ticker": ticker, "interval": interval, "candles": []}

@router.get("/{ticker}/intraday")
async def get_intraday(
    ticker: str = Path(..., min_length=1, max_length=4, regex=r"^[A-Z]+$")
):
    """Latest quote snapshot (bid, ask, last)."""
    return {"ticker": ticker, "bid": None, "ask": None, "last": None}

@router.websocket("/{ticker}/stream")
async def stream_ticks(websocket: WebSocket, ticker: str):
    """Real-time tick push (JSON frames)."""
    await websocket.accept()
    await websocket.send_json({"ts": "2025-07-08T14:33:05.215Z", "price": 0, "volume": 0})
    await websocket.close()



