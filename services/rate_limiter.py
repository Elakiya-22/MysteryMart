import time
from collections import defaultdict
from typing import Dict, List, Tuple
from flask import request, abort


class RateLimiter:
    """Lightweight in-memory sliding window rate limiter for Flask endpoints."""
    def __init__(self):
        # Key: (endpoint_name, ip_address) -> list of request timestamps
        self._history: Dict[Tuple[str, str], List[float]] = defaultdict(list)

    def is_allowed(self, key: str, max_requests: int, window_seconds: int = 60) -> bool:
        """Check if request from client IP is allowed within sliding window."""
        now = time.time()
        client_ip = request.headers.get('X-Forwarded-For', request.remote_addr or '127.0.0.1').split(',')[0].strip()
        storage_key = (key, client_ip)

        # Evict timestamps older than the window
        timestamps = self._history[storage_key]
        cutoff = now - window_seconds
        valid_timestamps = [t for t in timestamps if t > cutoff]

        if len(valid_timestamps) >= max_requests:
            self._history[storage_key] = valid_timestamps
            return False

        valid_timestamps.append(now)
        self._history[storage_key] = valid_timestamps
        return True

    def limit(self, key: str, max_requests: int = 15, window_seconds: int = 60):
        """Decorator or direct checker for route handler."""
        if not self.is_allowed(key, max_requests, window_seconds):
            abort(429)


rate_limiter = RateLimiter()
