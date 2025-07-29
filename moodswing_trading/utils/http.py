import hashlib
import json
from typing import Any, Dict

from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse


def cached_json_response(data: Any, cache_seconds: int) -> JSONResponse:
    """Return JSONResponse with ETag and Cache-Control headers."""
    obj = jsonable_encoder(data)
    body = json.dumps(obj, separators=(",", ":"), sort_keys=True).encode()
    etag = hashlib.sha1(body).hexdigest()
    headers: Dict[str, str] = {
        "ETag": etag,
        "Cache-Control": f"public, max-age={cache_seconds}",
    }
    return JSONResponse(content=obj, headers=headers)