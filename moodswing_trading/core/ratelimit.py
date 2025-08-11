import time
from typing import Dict, Tuple
from fastapi import Request
from fastapi.responses import JSONResponse
from models import ProblemDetails

class SimpleRateLimiter:
    def __init__(self, limit: int = 60, window_seconds: int = 60):
        self.limit = limit
        self.window = window_seconds
        self.requests: Dict[str, Tuple[int, float]] = {}

    def _check(self, key: str) -> Tuple[int, float, bool]:
        # Use wall-clock time so X-RateLimit-Reset can be emitted as epoch seconds
        now = time.time()
        count, reset = self.requests.get(key, (0, now + self.window))
        if now >= reset:
            count = 0
            reset = now + self.window
        allowed = count < self.limit
        if allowed:
            count += 1
            self.requests[key] = (count, reset)
        return count, reset, allowed

    def headers(self, count: int, reset_epoch_seconds: float, limited: bool) -> Dict[str, str]:
        remaining = max(self.limit - count, 0)
        headers: Dict[str, str] = {
            "X-RateLimit-Limit": str(self.limit),
            "X-RateLimit-Remaining": str(remaining),
            # De-facto convention: epoch seconds when the window resets
            "X-RateLimit-Reset": str(int(reset_epoch_seconds)),
        }
        if limited:
            retry_after = max(int(reset_epoch_seconds - time.time()), 0)
            headers["Retry-After"] = str(retry_after)
        return headers


rate_limiter = SimpleRateLimiter()


async def rate_limit_middleware(request: Request, call_next):
    key = request.client.host if request.client else "anonymous"
    count, reset, allowed = rate_limiter._check(key)
    if not allowed:
        headers = rate_limiter.headers(count, reset, limited=True)
        problem = ProblemDetails(
            title="Too Many Requests", status=429, detail="Rate limit exceeded"
        )
        return JSONResponse(
            status_code=429,
            content=problem.model_dump(),
            headers=headers,
            media_type="application/problem+json",
        )
    response = await call_next(request)
    for k, v in rate_limiter.headers(count, reset, limited=False).items():
        response.headers[k] = v
    return response