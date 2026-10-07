import time
from collections import defaultdict, deque
from threading import Lock

from .config import settings


class RateLimiter:
    def __init__(self):
        self._hits = defaultdict(deque)
        self._lock = Lock()

    def allow(self, key: str) -> bool:
        now = time.time()
        cutoff = now - settings.rate_limit_window_seconds

        with self._lock:
            q = self._hits[key]
            while q and q[0] < cutoff:
                q.popleft()

            if len(q) >= settings.rate_limit_requests:
                return False

            q.append(now)
            return True


rate_limiter = RateLimiter()
