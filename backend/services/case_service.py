"""
Case Service
------------
Helpers for recording case timeline events and dispatching officer
notifications. Centralised so routers stay thin and behaviour is consistent.
"""

from typing import Optional, Dict, Any, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc

from models.case import CaseEvent, Notification
from models.officer import Officer


class CaseEventService:
    """Record and retrieve timeline events for a FIR case."""

    @staticmethod
    async def log_event(
        db: AsyncSession,
        fir_id: int,
        event_type: str,
        description: Optional[str] = None,
        officer_id: Optional[int] = None,
        metadata: Optional[Dict[str, Any]] = None,
        commit: bool = True,
    ) -> CaseEvent:
        """Append an event to a case timeline.

        Pass commit=False to batch the insert inside a larger transaction
        (e.g. bulk actions) and commit once at the end.
        """
        event = CaseEvent(
            fir_id=fir_id,
            event_type=event_type,
            description=description,
            officer_id=officer_id,
            event_metadata=metadata or {},
        )
        db.add(event)
        if commit:
            await db.commit()
            await db.refresh(event)
        return event

    @staticmethod
    async def get_timeline(
        db: AsyncSession,
        fir_id: int,
        limit: int = 100,
    ) -> List[CaseEvent]:
        """Return events for a FIR in chronological order (oldest first)."""
        result = await db.execute(
            select(CaseEvent)
            .where(CaseEvent.fir_id == fir_id)
            .order_by(CaseEvent.created_at.asc())
            .limit(limit)
        )
        return result.scalars().all()


class NotificationService:
    """Create and retrieve officer notifications."""

    @staticmethod
    async def notify(
        db: AsyncSession,
        officer_id: int,
        notification_type: str,
        title: str,
        message: Optional[str] = None,
        related_fir_id: Optional[int] = None,
        commit: bool = True,
    ) -> Notification:
        """Create a notification for a single officer."""
        notification = Notification(
            officer_id=officer_id,
            notification_type=notification_type,
            title=title,
            message=message,
            related_fir_id=related_fir_id,
        )
        db.add(notification)
        if commit:
            await db.commit()
            await db.refresh(notification)
        return notification

    @staticmethod
    async def broadcast(
        db: AsyncSession,
        notification_type: str,
        title: str,
        message: Optional[str] = None,
        related_fir_id: Optional[int] = None,
        exclude_officer_id: Optional[int] = None,
    ) -> int:
        """Send a notification to every active officer. Returns the count sent."""
        result = await db.execute(select(Officer).where(Officer.is_active == True))  # noqa: E712
        officers = result.scalars().all()

        sent = 0
        for officer in officers:
            if exclude_officer_id and officer.id == exclude_officer_id:
                continue
            db.add(Notification(
                officer_id=officer.id,
                notification_type=notification_type,
                title=title,
                message=message,
                related_fir_id=related_fir_id,
            ))
            sent += 1

        await db.commit()
        return sent

    @staticmethod
    async def list_for_officer(
        db: AsyncSession,
        officer_id: int,
        unread_only: bool = False,
        limit: int = 50,
    ) -> List[Notification]:
        query = select(Notification).where(Notification.officer_id == officer_id)
        if unread_only:
            query = query.where(Notification.is_read == False)  # noqa: E712
        result = await db.execute(
            query.order_by(desc(Notification.created_at)).limit(limit)
        )
        return result.scalars().all()

    @staticmethod
    async def unread_count(db: AsyncSession, officer_id: int) -> int:
        from sqlalchemy import func
        result = await db.execute(
            select(func.count(Notification.id)).where(
                (Notification.officer_id == officer_id)
                & (Notification.is_read == False)  # noqa: E712
            )
        )
        return result.scalar() or 0
