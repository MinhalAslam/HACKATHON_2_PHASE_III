from fastapi import HTTPException, Request, status
from collections import defaultdict
from datetime import datetime, timedelta
import time


class RateLimiter:
    """
    Simple in-memory rate limiter.
    In production, you'd use redis or similar for distributed rate limiting.
    """

    def __init__(self, max_requests: int = 10, window_seconds: int = 60):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests = defaultdict(list)

    def is_allowed(self, identifier: str) -> bool:
        """
        Check if the request is allowed based on rate limits.

        Args:
            identifier: A unique identifier for the client (e.g., IP address)

        Returns:
            True if request is allowed, False otherwise
        """
        now = time.time()
        # Clean old requests outside the window
        self.requests[identifier] = [
            req_time for req_time in self.requests[identifier]
            if now - req_time < self.window_seconds
        ]

        # Check if under limit
        if len(self.requests[identifier]) < self.max_requests:
            self.requests[identifier].append(now)
            return True

        return False


# Global rate limiter instance
rate_limiter = RateLimiter(max_requests=20, window_seconds=60)


def rate_limit_middleware(request: Request) -> None:
    """
    Rate limiting middleware function.
    Call this in endpoints that need rate limiting.
    """
    client_ip = request.client.host if request.client else "unknown"

    if not rate_limiter.is_allowed(client_ip):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded. Please try again later."
        )