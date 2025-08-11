"""Simple Redis JSON cache helpers with TTL.

Usage:
    from utils.cache import get_cache, get_json, set_json
"""

from __future__ import annotations

import json
from functools import lru_cache
from typing import Any, Optional

import redis.asyncio as redis

from core.config import get_settings


@lru_cache()
def get_cache() -> redis.Redis:
    settings = get_settings()
    return redis.from_url(settings.redis_url)


async def get_json(key: str) -> Optional[Any]:
    client = get_cache()
    try:
        data = await client.get(key)
        if not data:
            return None
        if isinstance(data, (bytes, bytearray)):
            data = data.decode()
        try:
            return json.loads(data)
        except Exception:
            return None
    except Exception:
        # Redis unavailable or connection error → treat as cache miss
        return None


async def set_json(key: str, value: Any, ttl_seconds: int) -> None:
    client = get_cache()
    try:
        await client.set(key, json.dumps(value), ex=ttl_seconds)
    except Exception:
        # best-effort cache
        pass




