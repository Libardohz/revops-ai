"""Thread-safe Sliding Window Rate Limiter & Brute-Force Protection for hzSaaS."""

import time
from collections import defaultdict
from threading import Lock
from typing import Optional
from fastapi import Request


class SlidingWindowRateLimiter:
    """In-memory sliding window rate limiter and failed-attempt lockout."""

    def __init__(self) -> None:
        self._lock = Lock()
        self._hits: dict[str, list[float]] = defaultdict(list)
        self._failures: dict[str, list[float]] = defaultdict(list)

    def is_rate_limited(self, key: str, max_requests: int, window_seconds: float) -> tuple[bool, int]:
        """Check if `key` has exceeded `max_requests` in `window_seconds`.

        Returns (is_limited, retry_after_seconds).
        """
        now = time.time()
        with self._lock:
            timestamps = [t for t in self._hits[key] if now - t < window_seconds]
            if len(timestamps) >= max_requests:
                earliest = min(timestamps)
                retry_after = max(1, int(window_seconds - (now - earliest)))
                self._hits[key] = timestamps
                return True, retry_after
            timestamps.append(now)
            self._hits[key] = timestamps
            return False, 0

    def record_failure(self, key: str) -> None:
        """Record an authentication or operation failure."""
        now = time.time()
        with self._lock:
            self._failures[key].append(now)

    def is_brute_force_locked(
        self, key: str, max_failures: int = 5, lock_window_seconds: float = 300.0
    ) -> tuple[bool, int]:
        """Check if `key` has >= max_failures within `lock_window_seconds`.

        Returns (is_locked, retry_after_seconds).
        """
        now = time.time()
        with self._lock:
            recent_fails = [t for t in self._failures[key] if now - t < lock_window_seconds]
            self._failures[key] = recent_fails
            if len(recent_fails) >= max_failures:
                earliest = min(recent_fails)
                retry_after = max(1, int(lock_window_seconds - (now - earliest)))
                return True, retry_after
            return False, 0

    def reset_failures(self, key: str) -> None:
        """Clear recorded failures on successful operation."""
        with self._lock:
            self._failures.pop(key, None)

    def clear(self) -> None:
        """Reset all rate limiter state (used in automated test suites)."""
        with self._lock:
            self._hits.clear()
            self._failures.clear()


# Global singleton instance
rate_limiter = SlidingWindowRateLimiter()


def get_client_ip(request: Optional[Request]) -> str:
    """Safely extract client IP from proxy headers (Cloudflare, Render) or direct socket."""
    if not request:
        return "127.0.0.1"
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        # First IP in the list is the originating client IP
        return forwarded.split(",")[0].strip()
    cf_ip = request.headers.get("cf-connecting-ip")
    if cf_ip:
        return cf_ip.strip()
    real_ip = request.headers.get("x-real-ip")
    if real_ip:
        return real_ip.strip()
    if request.client and request.client.host:
        return request.client.host
    return "127.0.0.1"

