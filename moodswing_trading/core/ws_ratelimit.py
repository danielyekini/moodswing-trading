"""Simple per-connection WebSocket rate meter and signaling.

Not strict enforcement; computes remaining tokens in the current window and
provides a helper to render a rate info frame.
"""

from __future__ import annotations

import time
from dataclasses import dataclass


@dataclass
class WsRateState:
    limit: int
    remaining: int
    reset_seconds: int


class WsRateLimiter:
    def __init__(self, limit: int = 60, window_seconds: int = 60) -> None:
        self.limit = limit
        self.window = window_seconds
        self._count = 0
        self._reset_at = time.monotonic() + self.window

    def tick(self) -> WsRateState:
        now = time.monotonic()
        if now >= self._reset_at:
            self._count = 0
            self._reset_at = now + self.window
        self._count += 1
        remaining = max(self.limit - self._count, 0)
        reset_seconds = max(int(self._reset_at - now), 0)
        return WsRateState(limit=self.limit, remaining=remaining, reset_seconds=reset_seconds)

    def snapshot(self) -> WsRateState:
        now = time.monotonic()
        if now >= self._reset_at:
            return WsRateState(limit=self.limit, remaining=self.limit, reset_seconds=self.window)
        remaining = max(self.limit - self._count, 0)
        reset_seconds = max(int(self._reset_at - now), 0)
        return WsRateState(limit=self.limit, remaining=remaining, reset_seconds=reset_seconds)








