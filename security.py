"""Optional API authentication and local, single-process request throttling."""

from collections import defaultdict, deque
import secrets
from threading import Lock
from time import monotonic

from fastapi import Header, HTTPException, Request

from config import get_settings

_hits: dict[str, deque] = defaultdict(deque)
_lock = Lock()


def protect(request: Request, x_api_key: str | None = Header(default=None)) -> None:
    settings = get_settings()
    expected = settings.backend_api_key.get_secret_value()
    if expected and not secrets.compare_digest((x_api_key or "").encode(), expected.encode()):
        raise HTTPException(401, "A valid X-API-Key header is required.")
    # Forwarded headers are deliberately not trusted. Production needs a shared limiter.
    host = request.client.host if request.client else "local"
    now = monotonic()
    with _lock:
        for key in list(_hits):
            if not _hits[key] or _hits[key][-1] <= now - 60:
                del _hits[key]
        if host not in _hits and len(_hits) >= 1024:
            raise HTTPException(429, "Server is busy. Try again in one minute.")
        queue = _hits[host]
        while queue and queue[0] <= now - 60:
            queue.popleft()
        if len(queue) >= settings.rate_limit_per_minute:
            raise HTTPException(429, "Too many requests. Try again in one minute.", headers={"Retry-After": "60"})
        queue.append(now)
