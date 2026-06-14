"""
CSRF Protection
---------------
Cross-Site Request Forgery (CSRF) token generation and validation.
"""

import secrets
import hashlib
import hmac
from datetime import datetime, timedelta
from typing import Optional, Tuple

# Store for active CSRF tokens (in production, use Redis)
_csrf_token_store = {}


class CSRFProtection:
    """CSRF token generation and validation."""

    TOKEN_EXPIRY_MINUTES = 60
    TOKEN_SIZE = 32  # bytes

    @staticmethod
    def generate_token() -> str:
        """Generate a CSRF token."""
        token = secrets.token_hex(CSRFProtection.TOKEN_SIZE)
        expiry = datetime.utcnow() + timedelta(minutes=CSRFProtection.TOKEN_EXPIRY_MINUTES)

        # Store token
        _csrf_token_store[token] = {
            "created_at": datetime.utcnow(),
            "expiry": expiry,
            "used": False,
        }

        # Clean up expired tokens periodically
        CSRFProtection._cleanup_expired_tokens()

        return token

    @staticmethod
    def validate_token(token: str) -> Tuple[bool, Optional[str]]:
        """
        Validate a CSRF token.

        Args:
            token: CSRF token to validate

        Returns:
            Tuple of (valid: bool, error_message: str)
        """
        if not token:
            return False, "CSRF token is required"

        if token not in _csrf_token_store:
            return False, "Invalid CSRF token"

        token_data = _csrf_token_store[token]

        # Check expiry
        if datetime.utcnow() > token_data["expiry"]:
            del _csrf_token_store[token]
            return False, "CSRF token has expired"

        # Check if already used
        if token_data["used"]:
            # Possible CSRF attack - token reuse
            del _csrf_token_store[token]
            return False, "CSRF token has already been used"

        # Mark as used
        token_data["used"] = True

        return True, None

    @staticmethod
    def _cleanup_expired_tokens() -> None:
        """Remove expired tokens from store."""
        now = datetime.utcnow()
        expired_tokens = [
            token
            for token, data in _csrf_token_store.items()
            if now > data["expiry"]
        ]
        for token in expired_tokens:
            del _csrf_token_store[token]

    @staticmethod
    def get_token_count() -> int:
        """Get number of active tokens (for monitoring)."""
        CSRFProtection._cleanup_expired_tokens()
        return len(_csrf_token_store)


class DoubleSubmitCookie:
    """Double submit cookie CSRF protection (alternative approach)."""

    SECRET_KEY = "firai-csrf-secret-key-change-in-production"

    @staticmethod
    def generate_token_pair() -> Tuple[str, str]:
        """
        Generate CSRF token for double-submit cookie pattern.

        Returns:
            Tuple of (cookie_value, form_token)
        """
        # Random value for cookie
        cookie_value = secrets.token_hex(32)

        # HMAC for form token
        form_token = hmac.new(
            DoubleSubmitCookie.SECRET_KEY.encode(),
            cookie_value.encode(),
            hashlib.sha256,
        ).hexdigest()

        return cookie_value, form_token

    @staticmethod
    def validate_token_pair(
        cookie_value: str, form_token: str
    ) -> Tuple[bool, Optional[str]]:
        """
        Validate CSRF token pair.

        Args:
            cookie_value: Value from CSRF cookie
            form_token: Value from form/request

        Returns:
            Tuple of (valid: bool, error_message: str)
        """
        if not cookie_value or not form_token:
            return False, "CSRF token is required"

        # Compute expected form token
        expected_form_token = hmac.new(
            DoubleSubmitCookie.SECRET_KEY.encode(),
            cookie_value.encode(),
            hashlib.sha256,
        ).hexdigest()

        # Constant-time comparison to prevent timing attacks
        if not hmac.compare_digest(form_token, expected_form_token):
            return False, "Invalid CSRF token"

        return True, None
