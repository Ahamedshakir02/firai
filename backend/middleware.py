"""
Middleware for Request/Response Logging and Metrics
---------------------------------------------------
Captures request timing, logs API calls, and records metrics.
"""

import time
from typing import Callable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from logging_config import api_logger


class LoggingMiddleware(BaseHTTPMiddleware):
    """Middleware to log API requests and responses."""

    async def dispatch(
        self, request: Request, call_next: Callable
    ) -> Response:
        start_time = time.time()

        # Get client IP
        client_ip = request.client.host if request.client else "unknown"

        # Prepare response
        response = await call_next(request)

        # Calculate duration
        duration_ms = (time.time() - start_time) * 1000

        # Log API call
        api_logger.api_call(
            method=request.method,
            endpoint=request.url.path,
            status_code=response.status_code,
            duration_ms=duration_ms,
            user_id=getattr(request.state, "officer_id", None),
            error=None if response.status_code < 400 else f"HTTP {response.status_code}",
        )

        # Add performance header
        response.headers["X-Process-Time"] = str(duration_ms)

        return response


class ErrorCatchingMiddleware(BaseHTTPMiddleware):
    """Middleware to catch and log unhandled exceptions."""

    async def dispatch(
        self, request: Request, call_next: Callable
    ) -> Response:
        try:
            response = await call_next(request)
            return response
        except Exception as e:
            # Log the exception
            from logging_config import logger

            logger.log_with_extra(
                level=40,  # ERROR
                message=f"Unhandled exception in {request.method} {request.url.path}",
                extra={
                    "type": "unhandled_exception",
                    "exception": str(e),
                    "method": request.method,
                    "path": request.url.path,
                    "client_ip": request.client.host if request.client else "unknown",
                },
            )

            # Re-raise so FastAPI can handle it
            raise


class PerformanceMonitoringMiddleware(BaseHTTPMiddleware):
    """Middleware to monitor and alert on slow requests."""

    SLOW_REQUEST_THRESHOLD_MS = 5000  # 5 seconds

    async def dispatch(
        self, request: Request, call_next: Callable
    ) -> Response:
        start_time = time.time()
        response = await call_next(request)
        duration_ms = (time.time() - start_time) * 1000

        # Log slow requests
        if duration_ms > self.SLOW_REQUEST_THRESHOLD_MS:
            from logging_config import logger

            logger.performance_warning(
                component="api",
                metric=f"{request.method} {request.url.path}",
                value=duration_ms,
                threshold=self.SLOW_REQUEST_THRESHOLD_MS,
            )

        return response
