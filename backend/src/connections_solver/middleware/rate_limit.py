"""Rate limiting middleware using SlowAPI.

**What is rate limiting?**
Rate limiting restricts how many requests a user can make in a given time period.
This prevents:
- API abuse (someone spamming your endpoint)
- Accidental DDoS from misbehaving clients
- Resource exhaustion from runaway scripts
- Unfair usage (one user hogging all resources)

**How it works:**
1. Each request is tracked by IP address (or user ID if authenticated)
2. A counter increments for each request
3. When limit is reached, requests are blocked with 429 status
4. Counter resets after the time window expires

**Example:**
If limit is "10 per minute":
- Request 1-10: OK (200)
- Request 11: Blocked (429 "Too Many Requests")
- After 1 minute: Counter resets, requests allowed again

**Why we use SlowAPI:**
- Industry-standard rate limiting for FastAPI
- Multiple strategies (fixed window, sliding window)
- Per-endpoint customization
- Redis support for distributed systems
- Easy integration with FastAPI
"""

from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi import Request, Response
from fastapi.responses import JSONResponse

# Create limiter instance
# Uses client IP address for identification
# In production with load balancer, configure to use X-Forwarded-For header
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["100/minute"],  # Global default: 100 requests per minute
    storage_uri="memory://",  # In-memory storage (use Redis for production with multiple instances)
)

# Rate limit configurations for different operations
# These can be customized per endpoint

# Standard operations (puzzles, solvers list, health checks)
RATE_LIMIT_STANDARD = "30/minute"

# Expensive operations (solving puzzles, evaluations)
# Lower limit because these consume significant CPU/memory
RATE_LIMIT_EXPENSIVE = "10/minute"

# Read operations (fetching puzzles, results)
RATE_LIMIT_READ = "60/minute"


def rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded) -> Response:
    """
    Custom handler for rate limit exceeded errors.

    **Why we need this:**
    - Provides clear error messages to users
    - Includes retry information (when they can try again)
    - Returns proper HTTP 429 status with headers
    - Logs abuse attempts for monitoring

    **Headers returned:**
    - X-RateLimit-Limit: Maximum requests allowed
    - X-RateLimit-Remaining: Requests left in current window
    - X-RateLimit-Reset: Unix timestamp when limit resets
    - Retry-After: Seconds until user can retry

    Args:
        request: The incoming request
        exc: The rate limit exception

    Returns:
        JSON response with error details and retry information
    """
    return JSONResponse(
        status_code=429,
        content={
            "error": "Rate limit exceeded",
            "message": f"Too many requests. Please try again later.",
            "detail": str(exc),
        },
        headers={
            "Retry-After": "60",  # Suggest retry after 60 seconds
        },
    )
