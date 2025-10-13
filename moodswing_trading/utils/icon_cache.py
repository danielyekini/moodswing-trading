from __future__ import annotations

from typing import Optional, Tuple

import redis.asyncio as redis

from core.config import get_settings


SUCCESS_TTL_SECONDS = 30 * 24 * 60 * 60  # 30 days
NEGATIVE_TTL_SECONDS = 24 * 60 * 60      # 24 hours


def _keys(domain: str) -> tuple[str, str, str]:
    base = f"icon:{domain}"
    return f"{base}:bytes", f"{base}:ct", f"{base}:neg"


_client: redis.Redis | None = None


def _get_client() -> redis.Redis:
    global _client
    if _client is None:
        settings = get_settings()
        _client = redis.from_url(settings.redis_url)
    return _client


async def get_cached_icon(domain: str) -> Optional[Tuple[bytes, str]]:
    client = _get_client()
    data_key, ct_key, neg_key = _keys(domain)
    # Negative cache check
    try:
        neg = await client.get(neg_key)
        if neg:
            return None
    except Exception:
        pass

    try:
        payload, content_type = await client.get(data_key), await client.get(ct_key)
        if payload and content_type:
            if isinstance(content_type, (bytes, bytearray)):
                content_type = content_type.decode()
            return bytes(payload), str(content_type)
    except Exception:
        pass
    return None


async def set_cached_icon(domain: str, payload: bytes, content_type: str) -> None:
    client = _get_client()
    data_key, ct_key, neg_key = _keys(domain)
    try:
        # Clear any negative cache
        try:
            await client.delete(neg_key)
        except Exception:
            pass
        # Store bytes and content-type with TTL
        await client.set(data_key, payload, ex=SUCCESS_TTL_SECONDS)
        await client.set(ct_key, content_type, ex=SUCCESS_TTL_SECONDS)
    except Exception:
        # best-effort
        pass


async def set_negative_cache(domain: str) -> None:
    client = _get_client()
    _, _, neg_key = _keys(domain)
    try:
        await client.set(neg_key, b"1", ex=NEGATIVE_TTL_SECONDS)
    except Exception:
        pass


