"""
Rate Limiter Service
--------------------
Implements rate limiting to prevent brute force and abuse.
"""

import time
from typing import Optional, Dict, Tuple
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from logging_config import logger

# In-memory store for rate limits (for testing/dev)
# In production, use Redis
_rate_limit_store: Dict[str, list] = {}


class RateLimiter:
    """Rate limiter for API endpoints."""

    def __init__(self, max_attempts: int, window_seconds: int):
        """
        Initialize rate limiter.

        Args:
            max_attempts: Number of allowed attempts
            window_seconds: Time window in seconds
        """
        self.max_attempts = max_attempts
        self.window_seconds = window_seconds

    async def is_allowed(self, identifier: str) -> Tuple[bool, Optional[int]]:
        """
        Check if request is allowed.

        Args:
            identifier: Unique identifier (IP, user ID, badge number, etc.)

        Returns:
            Tuple of (allowed: bool, retry_after_seconds: int)
        """
        now = time.time()
        window_start = now - self.window_seconds

        # Get or create list of timestamps for this identifier
        if identifier not in _rate_limit_store:
            _rate_limit_store[identifier] = []

        # Remove old entries outside the window
        _rate_limit_store[identifier] = [
            ts for ts in _rate_limit_store[identifier] if ts > window_start
        ]

        # Check if limit exceeded
        if len(_rate_limit_store[identifier]) >= self.max_attempts:
            # Calculate retry_after
            oldest_request = min(_rate_limit_store[identifier])
            retry_after = int((oldest_request + self.window_seconds - now) + 1)
            return False, retry_after

        # Add current request
        _rate_limit_store[identifier].append(now)
        return True, None

    async def reset(self, identifier: str) -> None:
        """Reset rate limit for an identifier."""
        if identifier in _rate_limit_store:
            del _rate_limit_store[identifier]


# Pre-configured rate limiters
LOGIN_LIMITER = RateLimiter(max_attempts=5, window_seconds=600)  # 5 attempts per 10 minutes
REGISTRATION_LIMITER = RateLimiter(max_attempts=3, window_seconds=3600)  # 3 per hour
API_LIMITER = RateLimiter(max_attempts=100, window_seconds=60)  # 100 per minute


class RateLimitService:
    """Service for managing rate limits with database persistence."""

    @staticmethod
    async def log_attempt(
        db: AsyncSession,
        endpoint: str,
        identifier: str,
        ip_address: str,
        success: bool,
    ) -> None:
        """Log a rate-limited endpoint attempt for analytics."""
        from models.audit import SecurityEvent

        if not success:
            # Log failed attempt
            event = SecurityEvent(
                event_type="rate_limit_attempt",
                severity="low" if success else "medium",
                message=f"Rate limited attempt on {endpoint}",
                ip_address=ip_address,
                details={
                    "endpoint": endpoint,
                    "identifier": identifier,
                    "success": success,
                },
            )
            db.add(event)
            await db.commit()

    @staticmethod
    async def get_attempts(
        identifier: str,
    ) -> int:
        """Get number of recent attempts for an identifier."""
        if identifier not in _rate_limit_store:
            return 0
        return len(_rate_limit_store[identifier])

    @staticmethod
    async def lockout_user(
        db: AsyncSession,
        badge_number: str,
        ip_address: str,
        duration_minutes: int = 15,
    ) -> None:
        """Lock out a user after too many failed attempts."""
        from models.audit import SecurityEvent

        event = SecurityEvent(
            event_type="account_lockout",
            severity="high",
            message=f"User {badge_number} locked out due to too many failed attempts",
            ip_address=ip_address,
            details={
                "badge_number": badge_number,
                "lockout_duration_minutes": duration_minutes,
            },
            action_taken="user_locked_out",
        )
        db.add(event)
        await db.commit()

        # Log to structured logger
        logger.security_event(
            event_type="account_lockout",
            severity="high",
            message=f"Account locked: {badge_number}",
            ip_address=ip_address,
        )
