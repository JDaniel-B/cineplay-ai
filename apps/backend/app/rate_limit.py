from collections import defaultdict, deque
from threading import Lock
from time import monotonic

from fastapi import HTTPException, status


class SlidingWindowLimiter:
    def __init__(self, limit: int, seconds: int) -> None:
        self.limit = limit
        self.seconds = seconds
        self._events: dict[str, deque[float]] = defaultdict(deque)
        self._lock = Lock()

    def check(self, key: str) -> None:
        now = monotonic()
        cutoff = now - self.seconds
        with self._lock:
            events = self._events[key]
            while events and events[0] < cutoff:
                events.popleft()
            if len(events) >= self.limit:
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail="Demasiadas solicitudes. Intenta de nuevo más tarde.",
                )
            events.append(now)


login_limiter = SlidingWindowLimiter(limit=8, seconds=60)
chat_limiter = SlidingWindowLimiter(limit=20, seconds=60)
