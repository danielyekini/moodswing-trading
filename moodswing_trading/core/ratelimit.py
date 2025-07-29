import time
from typing import Dict, Tuple
from fastapi import Request, Response

class SimpleRateLimiter:
    def __init__(self, limit: int = 60, window_seconds: int = 60):
        self.limit = limit
        self.window = window_seconds
        self.requests: Dict[str, Tuple[int, float]] = {}

    def _check(self, key: str) -> Tuple[int, float, bool]:
        now = time.monotonic()
        count, reset = self.requests.get(key, (0, now + self.window))
        if now >= reset:
            count = 0
            reset = now + self.window
        allowed = count < self.limit
        if allowed:
            count += 1
            self.requests[key] = (count, reset)
        return count, reset, allowed

    def headers(self, count: int, reset: float) -> Dict[str, str]:
        remaining = max(self.limit - count, 0)
        retry_after = max(int(reset - time.monotonic()), 0)
        return {
            "X-RateLimit-Limit": str(self.limit),
            "X-RateLimit-Remaining": str(remaining),
            "Retry-After": str(retry_after),
        }

rate_limiter = SimpleRateLimiter()

async def rate_limit_middleware(request: Request, call_next):
    key = request.client.host if request.client else "anonymous"
    count, reset, allowed = rate_limiter._check(key)
    if not allowed:
        headers = rate_limiter.headers(count, reset)
        return Response(status_code=429, content="Too Many Requests", headers=headers)
    response = await call_next(request)
    for k, v in rate_limiter.headers(count, reset).items():
        response.headers[k] = v
    return response