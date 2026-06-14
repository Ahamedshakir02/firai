"""
Logging Configuration for FirAI
--------------------------------
Structured JSON logging with audit trails, performance metrics, and error tracking.
"""

import logging
import json
import sys
from datetime import datetime
from typing import Any, Dict, Optional
from functools import wraps
import time

# Configure root logger
logging.basicConfig(
    level=logging.DEBUG,
    format="%(message)s",
    stream=sys.stdout,
)


class StructuredFormatter(logging.Formatter):
    """Convert log records to structured JSON."""

    def format(self, record: logging.LogRecord) -> str:
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }

        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)

        # Add custom fields if present
        if hasattr(record, "extra_data"):
            log_data.update(record.extra_data)

        return json.dumps(log_data)


class StructuredLogger(logging.Logger):
    """Custom logger with structured logging methods."""

    def __init__(self, name: str, level: int = logging.NOTSET):
        super().__init__(name, level)
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(StructuredFormatter())
        self.addHandler(handler)

    def log_with_extra(
        self,
        level: int,
        message: str,
        extra: Optional[Dict[str, Any]] = None,
        **kwargs,
    ):
        """Log with additional structured data."""
        record = self.makeRecord(
            self.name, level, "", 0, message, args=(), exc_info=None
        )
        if extra:
            record.extra_data = {**extra, **kwargs}
        else:
            record.extra_data = kwargs
        self.handle(record)

    def api_call(
        self,
        method: str,
        endpoint: str,
        status_code: int,
        duration_ms: float,
        user_id: Optional[str] = None,
        error: Optional[str] = None,
    ):
        """Log API call with metrics."""
        self.log_with_extra(
            logging.INFO,
            f"API {method} {endpoint}",
            extra={
                "type": "api_call",
                "method": method,
                "endpoint": endpoint,
                "status_code": status_code,
                "duration_ms": duration_ms,
                "user_id": user_id,
                "error": error,
            },
        )

    def fir_analysis(
        self,
        fir_id: int,
        crime_type: str,
        severity: str,
        confidence: Optional[float] = None,
        duration_ms: Optional[float] = None,
    ):
        """Log FIR analysis."""
        self.log_with_extra(
            logging.INFO,
            f"FIR analysis completed: {fir_id}",
            extra={
                "type": "fir_analysis",
                "fir_id": fir_id,
                "crime_type": crime_type,
                "severity": severity,
                "confidence": confidence,
                "duration_ms": duration_ms,
            },
        )

    def model_inference(
        self,
        model_name: str,
        input_size: int,
        output: Dict[str, Any],
        duration_ms: float,
    ):
        """Log AI model inference."""
        self.log_with_extra(
            logging.DEBUG,
            f"Model inference: {model_name}",
            extra={
                "type": "model_inference",
                "model_name": model_name,
                "input_size": input_size,
                "output_keys": list(output.keys()),
                "duration_ms": duration_ms,
            },
        )

    def database_query(
        self,
        query_type: str,
        table: str,
        duration_ms: float,
        rows_affected: Optional[int] = None,
    ):
        """Log database query."""
        self.log_with_extra(
            logging.DEBUG,
            f"Database {query_type} on {table}",
            extra={
                "type": "database_query",
                "query_type": query_type,
                "table": table,
                "duration_ms": duration_ms,
                "rows_affected": rows_affected,
            },
        )

    def audit_trail(
        self,
        action: str,
        resource_type: str,
        resource_id: Any,
        user_id: str,
        details: Optional[Dict[str, Any]] = None,
        ip_address: Optional[str] = None,
    ):
        """Log audit trail for compliance."""
        self.log_with_extra(
            logging.WARNING,  # High priority for audit
            f"Audit: {action} on {resource_type}:{resource_id}",
            extra={
                "type": "audit_trail",
                "action": action,
                "resource_type": resource_type,
                "resource_id": resource_id,
                "user_id": user_id,
                "ip_address": ip_address,
                "details": details or {},
            },
        )

    def security_event(
        self,
        event_type: str,
        severity: str,
        message: str,
        details: Optional[Dict[str, Any]] = None,
        user_id: Optional[str] = None,
        ip_address: Optional[str] = None,
    ):
        """Log security events (rate limiting, auth failures, etc.)."""
        level = logging.CRITICAL if severity == "critical" else logging.WARNING
        self.log_with_extra(
            level,
            f"Security: {event_type} - {message}",
            extra={
                "type": "security_event",
                "event_type": event_type,
                "severity": severity,
                "user_id": user_id,
                "ip_address": ip_address,
                "details": details or {},
            },
        )

    def performance_warning(
        self,
        component: str,
        metric: str,
        value: float,
        threshold: float,
    ):
        """Log performance warnings when metrics exceed thresholds."""
        self.log_with_extra(
            logging.WARNING,
            f"Performance: {component} {metric} exceeded threshold",
            extra={
                "type": "performance_warning",
                "component": component,
                "metric": metric,
                "value": value,
                "threshold": threshold,
            },
        )


# Set custom logger class
logging.setLoggerClass(StructuredLogger)

# Create logger instances
logger = logging.getLogger("firai")
api_logger = logging.getLogger("firai.api")
ai_logger = logging.getLogger("firai.ai")
db_logger = logging.getLogger("firai.db")
auth_logger = logging.getLogger("firai.auth")
audit_logger = logging.getLogger("firai.audit")


def log_execution_time(logger_instance: logging.Logger, component: str):
    """Decorator to log execution time of functions."""

    def decorator(func):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = await func(*args, **kwargs)
                duration_ms = (time.time() - start_time) * 1000
                logger_instance.log_with_extra(
                    logging.DEBUG,
                    f"Execution: {component}.{func.__name__}",
                    extra={
                        "type": "execution_time",
                        "component": component,
                        "function": func.__name__,
                        "duration_ms": duration_ms,
                        "status": "success",
                    },
                )
                return result
            except Exception as e:
                duration_ms = (time.time() - start_time) * 1000
                logger_instance.log_with_extra(
                    logging.ERROR,
                    f"Execution failed: {component}.{func.__name__}",
                    extra={
                        "type": "execution_time",
                        "component": component,
                        "function": func.__name__,
                        "duration_ms": duration_ms,
                        "status": "error",
                        "error": str(e),
                    },
                )
                raise

        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                duration_ms = (time.time() - start_time) * 1000
                logger_instance.log_with_extra(
                    logging.DEBUG,
                    f"Execution: {component}.{func.__name__}",
                    extra={
                        "type": "execution_time",
                        "component": component,
                        "function": func.__name__,
                        "duration_ms": duration_ms,
                        "status": "success",
                    },
                )
                return result
            except Exception as e:
                duration_ms = (time.time() - start_time) * 1000
                logger_instance.log_with_extra(
                    logging.ERROR,
                    f"Execution failed: {component}.{func.__name__}",
                    extra={
                        "type": "execution_time",
                        "component": component,
                        "function": func.__name__,
                        "duration_ms": duration_ms,
                        "status": "error",
                        "error": str(e),
                    },
                )
                raise

        # Return async or sync based on function
        import inspect

        if inspect.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper

    return decorator
