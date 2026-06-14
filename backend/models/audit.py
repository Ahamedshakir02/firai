"""
Audit Trail Models
------------------
Database models for compliance and security audit logging.
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, JSON, ForeignKey
from sqlalchemy.sql import func
from database import Base


class AuditLog(Base):
    """Audit trail for all important actions."""

    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)

    # User and action
    officer_id = Column(Integer, ForeignKey("officers.id", ondelete="SET NULL"), nullable=True)
    action = Column(String(100), nullable=False)  # login, logout, fir_view, fir_download, etc.

    # Resource being accessed
    resource_type = Column(String(100), nullable=False)  # fir, legal_section, pattern, etc.
    resource_id = Column(String(100), nullable=True)

    # Context
    ip_address = Column(String(45), nullable=True)  # IPv4 or IPv6
    user_agent = Column(Text, nullable=True)

    # Result
    status = Column(String(50), default="success")  # success, failure
    error_message = Column(Text, nullable=True)

    # Additional details
    details = Column(JSON, nullable=True)  # {query_params, data_accessed, etc.}

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)


class ErrorLog(Base):
    """Error and exception tracking."""

    __tablename__ = "error_logs"

    id = Column(Integer, primary_key=True, index=True)

    # Error details
    error_type = Column(String(100), nullable=False)  # ValueError, SQLError, etc.
    message = Column(Text, nullable=False)
    traceback = Column(Text, nullable=True)

    # Context
    component = Column(String(100), nullable=False)  # which service/route errored
    officer_id = Column(Integer, ForeignKey("officers.id", ondelete="SET NULL"), nullable=True)
    endpoint = Column(String(200), nullable=True)

    # Request context
    method = Column(String(10), nullable=True)  # GET, POST, etc.
    path = Column(String(500), nullable=True)
    ip_address = Column(String(45), nullable=True)

    # Additional data
    context = Column(JSON, nullable=True)  # request body, params, etc.

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    resolved_at = Column(DateTime(timezone=True), nullable=True)


class PerformanceMetric(Base):
    """Track performance metrics for optimization."""

    __tablename__ = "performance_metrics"

    id = Column(Integer, primary_key=True, index=True)

    # What was measured
    component = Column(String(100), nullable=False)  # api, ocr, embedding, etc.
    operation = Column(String(100), nullable=False)  # classify, search, etc.

    # Measurements
    duration_ms = Column(Integer, nullable=False)  # milliseconds
    input_size = Column(Integer, nullable=True)  # bytes or character count

    # Status
    status = Column(String(50), default="success")

    # Context
    details = Column(JSON, nullable=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)


class SecurityEvent(Base):
    """Track security-related events."""

    __tablename__ = "security_events"

    id = Column(Integer, primary_key=True, index=True)

    # Event details
    event_type = Column(String(100), nullable=False)  # login_failure, rate_limit_exceeded, etc.
    severity = Column(String(50), nullable=False)  # low, medium, high, critical
    message = Column(Text, nullable=False)

    # Who/where
    officer_id = Column(Integer, ForeignKey("officers.id", ondelete="SET NULL"), nullable=True)
    ip_address = Column(String(45), nullable=True)

    # Details
    details = Column(JSON, nullable=True)

    # Action taken
    action_taken = Column(String(200), nullable=True)  # blocked, logged, etc.

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
