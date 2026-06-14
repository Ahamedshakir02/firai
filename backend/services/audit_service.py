"""
Audit Service
-------------
Handle audit logging, error tracking, and compliance logging.
"""

from typing import Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc, func
from datetime import datetime, timedelta

from models.audit import AuditLog, ErrorLog, SecurityEvent, PerformanceMetric
from logging_config import audit_logger


class AuditService:
    """Service for audit trail and compliance logging."""

    @staticmethod
    async def log_action(
        db: AsyncSession,
        officer_id: Optional[int],
        action: str,
        resource_type: str,
        resource_id: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        status: str = "success",
        error_message: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ) -> AuditLog:
        """Log an action to audit trail."""
        audit_log = AuditLog(
            officer_id=officer_id,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            ip_address=ip_address,
            user_agent=user_agent,
            status=status,
            error_message=error_message,
            details=details or {},
        )
        db.add(audit_log)
        await db.commit()
        await db.refresh(audit_log)

        # Also log to structured logger
        audit_logger.audit_trail(
            action=action,
            resource_type=resource_type,
            resource_id=resource_id or "N/A",
            user_id=str(officer_id) if officer_id else "unknown",
            details=details,
            ip_address=ip_address,
        )

        return audit_log

    @staticmethod
    async def log_fir_access(
        db: AsyncSession,
        officer_id: int,
        fir_id: int,
        action: str,  # view, download, analyze, etc.
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> AuditLog:
        """Log FIR access."""
        return await AuditService.log_action(
            db=db,
            officer_id=officer_id,
            action=action,
            resource_type="fir",
            resource_id=str(fir_id),
            ip_address=ip_address,
            user_agent=user_agent,
            details={"fir_id": fir_id},
        )

    @staticmethod
    async def log_legal_query(
        db: AsyncSession,
        officer_id: int,
        query: str,
        ip_address: Optional[str] = None,
    ) -> AuditLog:
        """Log legal assistant query."""
        return await AuditService.log_action(
            db=db,
            officer_id=officer_id,
            action="legal_query",
            resource_type="legal_assistant",
            ip_address=ip_address,
            details={"query": query[:100]},  # Store first 100 chars
        )

    @staticmethod
    async def get_officer_activity(
        db: AsyncSession,
        officer_id: int,
        limit: int = 100,
    ) -> list[AuditLog]:
        """Retrieve activity history for an officer."""
        result = await db.execute(
            select(AuditLog)
            .where(AuditLog.officer_id == officer_id)
            .order_by(desc(AuditLog.created_at))
            .limit(limit)
        )
        return result.scalars().all()

    @staticmethod
    async def get_resource_access_history(
        db: AsyncSession,
        resource_type: str,
        resource_id: str,
        limit: int = 50,
    ) -> list[AuditLog]:
        """Retrieve who accessed a specific resource."""
        result = await db.execute(
            select(AuditLog)
            .where(
                (AuditLog.resource_type == resource_type)
                & (AuditLog.resource_id == resource_id)
            )
            .order_by(desc(AuditLog.created_at))
            .limit(limit)
        )
        return result.scalars().all()


class ErrorTrackingService:
    """Service for error tracking and alerting."""

    @staticmethod
    async def log_error(
        db: AsyncSession,
        error_type: str,
        message: str,
        component: str,
        traceback: Optional[str] = None,
        officer_id: Optional[int] = None,
        endpoint: Optional[str] = None,
        method: Optional[str] = None,
        path: Optional[str] = None,
        ip_address: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> ErrorLog:
        """Log an error."""
        error_log = ErrorLog(
            error_type=error_type,
            message=message,
            component=component,
            traceback=traceback,
            officer_id=officer_id,
            endpoint=endpoint,
            method=method,
            path=path,
            ip_address=ip_address,
            context=context or {},
        )
        db.add(error_log)
        await db.commit()
        await db.refresh(error_log)

        return error_log

    @staticmethod
    async def get_recent_errors(
        db: AsyncSession,
        component: Optional[str] = None,
        hours: int = 24,
        limit: int = 100,
    ) -> list[ErrorLog]:
        """Get recent errors."""
        query = select(ErrorLog)

        if component:
            query = query.where(ErrorLog.component == component)

        # Only last N hours
        since = datetime.utcnow() - timedelta(hours=hours)
        query = query.where(ErrorLog.created_at >= since)

        result = await db.execute(
            query.order_by(desc(ErrorLog.created_at)).limit(limit)
        )
        return result.scalars().all()

    @staticmethod
    async def mark_error_resolved(
        db: AsyncSession,
        error_id: int,
    ) -> ErrorLog:
        """Mark error as resolved."""
        result = await db.execute(select(ErrorLog).where(ErrorLog.id == error_id))
        error_log = result.scalar_one()
        error_log.resolved_at = datetime.utcnow()
        await db.commit()
        return error_log


class PerformanceTrackingService:
    """Service for performance metrics collection."""

    @staticmethod
    async def record_metric(
        db: AsyncSession,
        component: str,
        operation: str,
        duration_ms: int,
        input_size: Optional[int] = None,
        status: str = "success",
        details: Optional[Dict[str, Any]] = None,
    ) -> PerformanceMetric:
        """Record a performance metric."""
        metric = PerformanceMetric(
            component=component,
            operation=operation,
            duration_ms=duration_ms,
            input_size=input_size,
            status=status,
            details=details or {},
        )
        db.add(metric)
        await db.commit()
        await db.refresh(metric)

        # Log to audit logger
        from logging_config import logger

        logger.performance_warning(
            component=component,
            metric=operation,
            value=duration_ms,
            threshold=5000,  # Flag if > 5 seconds
        ) if duration_ms > 5000 else None

        return metric

    @staticmethod
    async def get_average_duration(
        db: AsyncSession,
        component: str,
        operation: str,
        hours: int = 24,
    ) -> Optional[float]:
        """Get average duration for an operation."""
        since = datetime.utcnow() - timedelta(hours=hours)
        result = await db.execute(
            select(func.avg(PerformanceMetric.duration_ms)).where(
                (PerformanceMetric.component == component)
                & (PerformanceMetric.operation == operation)
                & (PerformanceMetric.created_at >= since)
            )
        )
        return result.scalar()

    @staticmethod
    async def get_p95_duration(
        db: AsyncSession,
        component: str,
        operation: str,
        hours: int = 24,
    ) -> Optional[float]:
        """Get 95th percentile duration."""
        since = datetime.utcnow() - timedelta(hours=hours)
        # Note: Different DB backends have different percentile functions
        # This is a simplified version for PostgreSQL
        result = await db.execute(
            select(
                func.percentile_cont(0.95).within_group(
                    PerformanceMetric.duration_ms
                )
            ).where(
                (PerformanceMetric.component == component)
                & (PerformanceMetric.operation == operation)
                & (PerformanceMetric.created_at >= since)
            )
        )
        return result.scalar()


class SecurityEventService:
    """Service for security event tracking."""

    @staticmethod
    async def log_security_event(
        db: AsyncSession,
        event_type: str,
        severity: str,
        message: str,
        officer_id: Optional[int] = None,
        ip_address: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        action_taken: Optional[str] = None,
    ) -> SecurityEvent:
        """Log a security event."""
        event = SecurityEvent(
            event_type=event_type,
            severity=severity,
            message=message,
            officer_id=officer_id,
            ip_address=ip_address,
            details=details or {},
            action_taken=action_taken,
        )
        db.add(event)
        await db.commit()
        await db.refresh(event)

        # Also log to structured logger
        from logging_config import logger

        logger.security_event(
            event_type=event_type,
            severity=severity,
            message=message,
            details=details,
            user_id=str(officer_id) if officer_id else None,
            ip_address=ip_address,
        )

        return event

    @staticmethod
    async def log_auth_failure(
        db: AsyncSession,
        badge_number: str,
        ip_address: Optional[str] = None,
        reason: str = "invalid_credentials",
    ) -> SecurityEvent:
        """Log authentication failure."""
        return await SecurityEventService.log_security_event(
            db=db,
            event_type="auth_failure",
            severity="high",
            message=f"Failed login attempt for {badge_number}",
            ip_address=ip_address,
            details={"badge_number": badge_number, "reason": reason},
        )

    @staticmethod
    async def log_rate_limit_exceeded(
        db: AsyncSession,
        ip_address: str,
        endpoint: str,
    ) -> SecurityEvent:
        """Log rate limit exceeded."""
        return await SecurityEventService.log_security_event(
            db=db,
            event_type="rate_limit_exceeded",
            severity="medium",
            message=f"Rate limit exceeded for {endpoint}",
            ip_address=ip_address,
            action_taken="request_blocked",
        )

    @staticmethod
    async def get_security_events(
        db: AsyncSession,
        severity: Optional[str] = None,
        hours: int = 24,
        limit: int = 100,
    ) -> list[SecurityEvent]:
        """Get recent security events."""
        query = select(SecurityEvent)

        if severity:
            query = query.where(SecurityEvent.severity == severity)

        since = datetime.utcnow() - timedelta(hours=hours)
        query = query.where(SecurityEvent.created_at >= since)

        result = await db.execute(
            query.order_by(desc(SecurityEvent.created_at)).limit(limit)
        )
        return result.scalars().all()
