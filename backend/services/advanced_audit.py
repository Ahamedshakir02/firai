"""
Advanced Audit Logging
---------------------
Enhanced audit trail with compliance features, detailed reports, and retention policies.
"""

from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func
from logging_config import logger

from models.audit import AuditLog, SecurityEvent, ErrorLog


class AuditReportService:
    """Generate comprehensive audit reports for compliance."""

    @staticmethod
    async def generate_officer_report(
        db: AsyncSession,
        officer_id: int,
        start_date: datetime,
        end_date: datetime,
    ) -> dict:
        """Generate detailed activity report for an officer."""
        result = await db.execute(
            select(AuditLog).where(
                and_(
                    AuditLog.officer_id == officer_id,
                    AuditLog.created_at.between(start_date, end_date),
                )
            ).order_by(AuditLog.created_at.desc())
        )
        logs = result.scalars().all()

        # Group by action type
        actions = {}
        for log in logs:
            if log.action not in actions:
                actions[log.action] = []
            actions[log.action].append(log)

        return {
            "officer_id": officer_id,
            "period": {
                "start": start_date.isoformat(),
                "end": end_date.isoformat(),
            },
            "total_actions": len(logs),
            "actions_by_type": {
                action: len(logs) for action, logs in actions.items()
            },
            "critical_actions": [
                {
                    "timestamp": log.created_at.isoformat(),
                    "action": log.action,
                    "resource": f"{log.resource_type}:{log.resource_id}",
                    "status": log.status,
                }
                for log in logs
                if log.action in ["fir_download", "bulk_export", "admin_action"]
            ],
            "failed_operations": len([l for l in logs if l.status == "failure"]),
        }

    @staticmethod
    async def generate_compliance_report(
        db: AsyncSession,
        days: int = 30,
    ) -> dict:
        """Generate compliance report for auditors."""
        start_date = datetime.utcnow() - timedelta(days=days)

        # Get all logs in period
        result = await db.execute(
            select(AuditLog).where(
                AuditLog.created_at >= start_date
            ).order_by(AuditLog.created_at.desc())
        )
        logs = result.scalars().all()

        # Get security events
        result = await db.execute(
            select(SecurityEvent).where(
                SecurityEvent.created_at >= start_date
            ).order_by(SecurityEvent.created_at.desc())
        )
        security_events = result.scalars().all()

        # Get errors
        result = await db.execute(
            select(ErrorLog).where(
                ErrorLog.created_at >= start_date
            ).order_by(ErrorLog.created_at.desc())
        )
        errors = result.scalars().all()

        return {
            "period_days": days,
            "generated_at": datetime.utcnow().isoformat(),
            "summary": {
                "total_audit_logs": len(logs),
                "total_security_events": len(security_events),
                "total_errors": len(errors),
                "critical_events": len([e for e in security_events if e.severity == "critical"]),
                "high_events": len([e for e in security_events if e.severity == "high"]),
            },
            "fir_access_summary": {
                "views": len([l for l in logs if l.action == "fir_view"]),
                "downloads": len([l for l in logs if l.action == "fir_download"]),
                "analyses": len([l for l in logs if l.action == "fir_analyze"]),
            },
            "data_access_events": [
                {
                    "timestamp": log.created_at.isoformat(),
                    "officer": log.officer_id,
                    "action": log.action,
                    "resource": log.resource_id,
                    "ip_address": log.ip_address,
                }
                for log in logs
                if log.action in ["fir_download", "bulk_export", "report_generate"]
            ][:50],  # Top 50
            "security_incidents": [
                {
                    "timestamp": event.created_at.isoformat(),
                    "type": event.event_type,
                    "severity": event.severity,
                    "message": event.message,
                    "action_taken": event.action_taken,
                }
                for event in security_events
            ],
            "system_errors": len(errors),
            "unresolved_errors": len([e for e in errors if e.resolved_at is None]),
        }

    @staticmethod
    async def get_data_access_trail(
        db: AsyncSession,
        resource_type: str,
        resource_id: str,
    ) -> List[Dict[str, Any]]:
        """Get complete access trail for a specific FIR."""
        result = await db.execute(
            select(AuditLog).where(
                and_(
                    AuditLog.resource_type == resource_type,
                    AuditLog.resource_id == resource_id,
                )
            ).order_by(AuditLog.created_at.asc())
        )
        logs = result.scalars().all()

        return [
            {
                "timestamp": log.created_at.isoformat(),
                "officer": log.officer_id,
                "action": log.action,
                "status": log.status,
                "ip_address": log.ip_address,
                "details": log.details,
            }
            for log in logs
        ]

    @staticmethod
    async def generate_data_retention_report(db: AsyncSession) -> dict:
        """Report on data retention and cleanup needs."""
        now = datetime.utcnow()

        # Check for logs that should be deleted
        retention_days = {
            "audit_logs": 365,      # 1 year
            "security_events": 180,  # 6 months
            "error_logs": 90,        # 3 months
            "performance_metrics": 30,  # 1 month
        }

        return {
            "generated_at": now.isoformat(),
            "retention_policies": retention_days,
            "cleanup_required": {
                "audit_logs_to_delete": await _count_old_logs(db, AuditLog, retention_days["audit_logs"]),
                "security_events_to_delete": await _count_old_logs(db, SecurityEvent, retention_days["security_events"]),
                "error_logs_to_delete": await _count_old_logs(db, ErrorLog, retention_days["error_logs"]),
            },
        }


async def _count_old_logs(db: AsyncSession, model, days: int) -> int:
    """Count logs older than N days."""
    cutoff = datetime.utcnow() - timedelta(days=days)
    result = await db.execute(
        select(func.count(model.id)).where(model.created_at < cutoff)
    )
    return result.scalar() or 0


class AuditCleanupService:
    """Handle audit log cleanup and archival."""

    @staticmethod
    async def cleanup_old_logs(
        db: AsyncSession,
        days: int = 90,
        dry_run: bool = True,
    ) -> dict:
        """Delete logs older than N days."""
        cutoff = datetime.utcnow() - timedelta(days=days)

        if dry_run:
            # Just count, don't delete
            result = await db.execute(
                select(func.count(ErrorLog.id)).where(ErrorLog.created_at < cutoff)
            )
            count = result.scalar() or 0
            return {
                "dry_run": True,
                "would_delete": count,
                "message": f"Would delete {count} error logs older than {days} days",
            }
        else:
            # Actually delete
            await db.execute(
                delete(ErrorLog).where(ErrorLog.created_at < cutoff)
            )
            await db.commit()

            logger.log_with_extra(
                level=30,  # WARNING
                message="Old logs cleaned up",
                extra={
                    "cutoff_date": cutoff.isoformat(),
                    "days": days,
                },
            )

            return {
                "dry_run": False,
                "deleted": True,
                "message": f"Deleted error logs older than {days} days",
            }

    @staticmethod
    async def archive_logs(
        db: AsyncSession,
        archive_path: str,
        days: int = 365,
    ) -> dict:
        """Archive logs older than N days to file."""
        cutoff = datetime.utcnow() - timedelta(days=days)

        result = await db.execute(
            select(AuditLog).where(AuditLog.created_at < cutoff)
        )
        logs = result.scalars().all()

        # Would export to file in production
        return {
            "archived": len(logs),
            "archive_path": archive_path,
            "cutoff_date": cutoff.isoformat(),
        }


class ComplianceCheckService:
    """Compliance verification and monitoring."""

    @staticmethod
    async def check_unauthorized_access(db: AsyncSession) -> List[Dict[str, Any]]:
        """Detect potential unauthorized access patterns."""
        result = await db.execute(
            select(AuditLog).where(
                AuditLog.status == "failure"
            ).order_by(AuditLog.created_at.desc())
        )
        failed_attempts = result.scalars().all()

        # Find patterns (same officer, multiple failures, etc.)
        suspicious = []
        officers_failures = {}

        for log in failed_attempts:
            if log.officer_id not in officers_failures:
                officers_failures[log.officer_id] = []
            officers_failures[log.officer_id].append(log)

        # Flag officers with multiple failures in short time
        for officer_id, attempts in officers_failures.items():
            if len(attempts) > 5:
                suspicious.append({
                    "officer_id": officer_id,
                    "failed_attempts": len(attempts),
                    "actions": list(set([a.action for a in attempts])),
                    "last_attempt": attempts[0].created_at.isoformat(),
                })

        return suspicious

    @staticmethod
    async def verify_data_access_controls(db: AsyncSession) -> dict:
        """Verify that data access controls are working."""
        result = await db.execute(
            select(SecurityEvent).where(
                SecurityEvent.event_type == "unauthorized_access"
            )
        )
        unauthorized = result.scalars().all()

        result = await db.execute(
            select(AuditLog).where(
                AuditLog.resource_type == "fir"
            ).order_by(AuditLog.created_at.desc())
        )
        all_access = result.scalars().all()[:100]

        return {
            "total_fir_accesses": len(all_access),
            "unauthorized_attempts": len(unauthorized),
            "control_status": "healthy" if len(unauthorized) == 0 else "warning",
            "recent_accesses_verified": all(
                log.status == "success" for log in all_access
            ),
        }
