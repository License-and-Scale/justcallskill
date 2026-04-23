"""Token-bucket rate limiter.

Protects JustCall quota from runaway agent loops. Defaults to 60
requests per minute; override with JUSTCALL_RATE_LIMIT_PER_MIN.
"""

from __future__ import annotations

import os
import threading
import time

RATE_LIMIT = int(os.environ.get("JUSTCALL_RATE_LIMIT_PER_MIN", "60"))


class TokenBucket:
    def __init__(self, capacity: int = RATE_LIMIT, refill_per_sec: float | None = None) -> None:
        self.capacity = capacity
        self.refill_per_sec = refill_per_sec if refill_per_sec is not None else capacity / 60.0
        self._tokens = float(capacity)
        self._last = time.monotonic()
        self._lock = threading.Lock()

    def acquire(self, timeout: float = 30.0) -> None:
        deadline = time.monotonic() + timeout
        while True:
            with self._lock:
                now = time.monotonic()
                self._tokens = min(
                    self.capacity,
                    self._tokens + (now - self._last) * self.refill_per_sec,
                )
                self._last = now
                if self._tokens >= 1:
                    self._tokens -= 1
                    return
                wait = (1 - self._tokens) / self.refill_per_sec
            if time.monotonic() + wait > deadline:
                raise TimeoutError("rate-limit wait exceeded")
            time.sleep(min(wait, 0.25))


_bucket = TokenBucket()


def acquire() -> None:
    _bucket.acquire()
