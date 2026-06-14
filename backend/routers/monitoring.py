"""
Monitoring and Metrics Router
------------------------------
Endpoints for metrics, performance data, error tracking, and audit trails.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from datetime import datetime

from database import get_db
from routers.auth import get_current_officer
from services.audit_service import (
    AuditService,
    ErrorTrackingService,
    PerformanceTrackingService,
    SecurityEventService,
)
from models.officer import Officer
from logging_config import logger

router = APIRouter(prefix="/api/metrics", tags=["Monitoring"])


# ─────────────────────── Performance Metrics ───────────────────────


@router.get("/latency")
async def get_latency_metrics(
    db: AsyncSession = Depends(get_db),
    current_officer: Officer = Depends(get_current_officer),
    component: Optional[str] = None,
    operation: Optional[str] = None,
    hours: int = 24,
):
    """Get API and operation latency metrics."""
    if not current_officer.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can view metrics",
        )

    try:
        metrics = []

        if component and operation:
            avg = await PerformanceTrackingService.get_average_duration(
                db, component, operation, hours
            )
            p95 = await PerformanceTrackingService.get_p95_duration(
                db, component, operation, hours
            )
            metrics.append(
                {
                    "component": component,
                    "operation": operation,
                    "avg_ms": avg,
                    "p95_ms": p95,
                    "hours": hours,
                }
            )
        else:
            # Return general latency summary
            metrics.append(
                {
                    "message": "Specify component and operation for detailed metrics",
                }
            )

        return {"metrics": metrics}
    except Exception as e:
        logger.error(f"Failed to get latency metrics: {e}")
        raise HTTPException(
            status_code=500, detail="Failed to retrieve metrics"
        )


@router.get("/errors")
async def get_error_metrics(
    db: AsyncSession = Depends(get_db),
    current_officer: Officer = Depends(get_current_officer),
    component: Optional[str] = None,
    hours: int = 24,
):
    """Get error metrics and recent errors."""
    if not current_officer.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can view metrics",
        )

    try:
        errors = await ErrorTrackingService.get_recent_errors(
            db, component=component, hours=hours, limit=50
        )

        return {
            "total_errors": len(errors),
            "component": component,
            "hours": hours,
            "errors": [
                {
                    "id": e.id,
                    "error_type": e.error_type,
                    "message": e.message,
                    "component": e.component,
                    "created_at": e.created_at,
                    "resolved": e.resolved_at is not None,
                }
                for e in errors
            ],
        }
    except Exception as e:
        logger.error(f"Failed to get error metrics: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve errors")


@router.post("/errors/{error_id}/resolve")
async def resolve_error(
    error_id: int,
    db: AsyncSession = Depends(get_db),
    current_officer: Officer = Depends(get_current_officer),
):
    """Mark an error as resolved."""
    if not current_officer.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can resolve errors",
        )

    try:
        error = await ErrorTrackingService.mark_error_resolved(db, error_id)
        return {"status": "resolved", "error_id": error.id}
    except Exception as e:
        raise HTTPException(status_code=404, detail="Error not found")


# ─────────────────────── Audit Trail ───────────────────────


@router.get("/audit/my-activity")
async def get_my_activity(
    db: AsyncSession = Depends(get_db),
    current_officer: Officer = Depends(get_current_officer),
    limit: int = 100,
):
    """Get current officer's activity history."""
    try:
        activities = await AuditService.get_officer_activity(
            db, current_officer.id, limit
        )

        return {
            "officer_id": current_officer.id,
            "total_activities": len(activities),
            "activities": [
                {
                    "id": a.id,
                    "action": a.action,
                    "resource_type": a.resource_type,
                    "resource_id": a.resource_id,
                    "status": a.status,
                    "created_at": a.created_at,
                }
                for a in activities
            ],
        }
    except Exception as e:
        logger.error(f"Failed to retrieve activity: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve activity")


@router.get("/audit/resource/{resource_type}/{resource_id}")
async def get_resource_access_history(
    resource_type: str,
    resource_id: str,
    db: AsyncSession = Depends(get_db),
    current_officer: Officer = Depends(get_current_officer),
    limit: int = 50,
):
    """Get access history for a specific resource (admin only)."""
    if not current_officer.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can view resource access history",
        )

    try:
        accesses = await AuditService.get_resource_access_history(
            db, resource_type, resource_id, limit
        )

        return {
            "resource_type": resource_type,
            "resource_id": resource_id,
            "total_accesses": len(accesses),
            "accesses": [
                {
                    "id": a.id,
                    "officer_id": a.officer_id,
                    "action": a.action,
                    "status": a.status,
                    "ip_address": a.ip_address,
                    "created_at": a.created_at,
                }
                for a in accesses
            ],
        }
    except Exception as e:
        logger.error(f"Failed to retrieve access history: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve history")


# ─────────────────────── Security Events ───────────────────────


@router.get("/security/events")
async def get_security_events(
    db: AsyncSession = Depends(get_db),
    current_officer: Officer = Depends(get_current_officer),
    severity: Optional[str] = None,
    hours: int = 24,
):
    """Get security events (admin only)."""
    if not current_officer.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can view security events",
        )

    try:
        events = await SecurityEventService.get_security_events(
            db, severity=severity, hours=hours, limit=100
        )

        return {
            "total_events": len(events),
            "severity": severity,
            "hours": hours,
            "events": [
                {
                    "id": e.id,
                    "event_type": e.event_type,
                    "severity": e.severity,
                    "message": e.message,
                    "action_taken": e.action_taken,
                    "ip_address": e.ip_address,
                    "created_at": e.created_at,
                }
                for e in events
            ],
        }
    except Exception as e:
        logger.error(f"Failed to retrieve security events: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve events")


# ─────────────────────── Health & Status ───────────────────────


@router.get("/health")
async def health_check():
    """Quick health check with timestamp."""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
    }


@router.get("/status")
async def system_status(
    db: AsyncSession = Depends(get_db),
    current_officer: Officer = Depends(get_current_officer),
):
    """Get system status including recent errors and metrics."""
    if not current_officer.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can view system status",
        )

    try:
        recent_errors = await ErrorTrackingService.get_recent_errors(
            db, hours=1, limit=10
        )
        security_events = await SecurityEventService.get_security_events(
            db, hours=1, limit=10
        )

        return {
            "status": "operational",
            "timestamp": datetime.utcnow().isoformat(),
            "recent_errors": len(recent_errors),
            "critical_errors": len(
                [e for e in recent_errors if "critical" in e.error_type.lower()]
            ),
            "security_events": len(security_events),
            "high_severity_events": len(
                [e for e in security_events if e.severity == "high"]
            ),
        }
    except Exception as e:
        logger.error(f"Failed to get system status: {e}")
        return {
            "status": "error",
            "error": "Failed to retrieve status",
        }
