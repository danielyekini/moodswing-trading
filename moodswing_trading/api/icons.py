from __future__ import annotations

import re
from typing import Optional, Tuple
from urllib.parse import urlparse

import httpx
from fastapi import APIRouter, Path, Response
from fastapi.responses import StreamingResponse

from utils.icon_cache import get_cached_icon, set_cached_icon, set_negative_cache


router = APIRouter(
    prefix="/api/v1/icons",
    tags=["icons"],
)


DOMAIN_RE = re.compile(r"^[a-z0-9.-]+\.[a-z]{2,}$")
MAX_SIZE = 256 * 1024  # 256KB safety cap


def normalize_domain(domain: str) -> Optional[str]:
    d = domain.strip().lower()
    if d.startswith("http://") or d.startswith("https://"):
        d = urlparse(d).netloc
    if d.startswith("www."):
        d = d[4:]
    if not DOMAIN_RE.match(d):
        return None
    return d


async def _fetch_first_ok(urls: list[str]) -> Optional[Tuple[bytes, str]]:
    headers = {"User-Agent": "mst-favicon/1.0"}
    timeout = httpx.Timeout(3.0, connect=2.0)
    async with httpx.AsyncClient(timeout=timeout, headers=headers, follow_redirects=True) as client:
        for u in urls:
            try:
                r = await client.get(u)
                if r.status_code == 200 and r.content:
                    if len(r.content) > MAX_SIZE:
                        continue
                    ctype = r.headers.get("content-type", "application/octet-stream")
                    return r.content, ctype
            except Exception:
                continue
    return None


@router.get("/{domain}")
async def get_icon(domain: str = Path(...)) -> Response:
    """Return a site's favicon with long cache headers, caching in Redis."""
    d = normalize_domain(domain)
    if not d:
        return Response(status_code=400)

    # Cache hit
    cached = await get_cached_icon(d)
    if cached:
        payload, ctype = cached
        return StreamingResponse(iter([payload]), media_type=ctype, headers={
            "Cache-Control": "public, max-age=2592000",
        })

    # Try upstream resolvers in order
    urls = [
        f"https://www.google.com/s2/favicons?domain={d}&sz=64",
        f"https://icons.duckduckgo.com/ip3/{d}.ico",
        f"https://{d}/favicon.ico",
    ]
    fetched = await _fetch_first_ok(urls)
    if not fetched:
        await set_negative_cache(d)
        return Response(status_code=404)

    payload, ctype = fetched
    await set_cached_icon(d, payload, ctype)
    return StreamingResponse(iter([payload]), media_type=ctype, headers={
        "Cache-Control": "public, max-age=2592000",
    })


