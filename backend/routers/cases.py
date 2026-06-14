"""
Cases Router
------------
Case collaboration features:
  - Annotations / notes on FIR cases
  - Bulk actions (status change, tagging, delete)
  - Case timeline (event history)
  - Officer notifications / alerts

All endpoints require a valid officer JWT.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update

from database import get_db
from models.fir import FIR
from models.case import FIRNote, Notification
from models.officer import Officer
from schemas.case import (
    NoteCreate, NoteUpdate, NoteResponse,
    BulkActionRequest, BulkActionResponse,
    CaseEventResponse, NotificationResponse,
)
from services.case_service import CaseEventService, NotificationService
from routers.auth import require_officer

router = APIRouter(prefix="/api/cases", tags=["Cases"], dependencies=[Depends(require_officer)])

VALID_STATUSES = {"new", "under_investigation", "charge_sheeted", "closed"}


# ──────────────────────── Notes / Annotations ────────────────────────

def _note_to_response(note: FIRNote, officer: Officer) -> NoteResponse:
    return NoteResponse(
        id=note.id,
        fir_id=note.fir_id,
        officer_id=note.officer_id,
        author_name=note.author_name,
        text=note.text,
        created_at=note.created_at,
        updated_at=note.updated_at,
        can_edit=(officer.is_admin or note.officer_id == officer.id),
    )


@router.get("/{fir_id}/notes", response_model=List[NoteResponse])
async def list_notes(
    fir_id: int,
    db: AsyncSession = Depends(get_db),
    officer: Officer = Depends(require_officer),
):
    """List all notes on a FIR, newest first."""
    result = await db.execute(
        select(FIRNote).where(FIRNote.fir_id == fir_id).order_by(FIRNote.created_at.desc())
    )
    notes = result.scalars().all()
    return [_note_to_response(n, officer) for n in notes]


@router.post("/{fir_id}/notes", response_model=NoteResponse)
async def create_note(
    fir_id: int,
    body: NoteCreate,
    db: AsyncSession = Depends(get_db),
    officer: Officer = Depends(require_officer),
):
    """Add a note to a FIR case. Records a timeline event."""
    # Ensure the FIR exists
    fir = (await db.execute(select(FIR).where(FIR.id == fir_id))).scalar_one_or_none()
    if not fir:
        raise HTTPException(status_code=404, detail="FIR not found")

    note = FIRNote(
        fir_id=fir_id,
        officer_id=officer.id,
        author_name=officer.name,
        text=body.text.strip(),
    )
    db.add(note)
    await db.flush()

    await CaseEventService.log_event(
        db, fir_id=fir_id, event_type="note_added",
        description=f"{officer.name} added a note",
        officer_id=officer.id, commit=False,
    )
    await db.commit()
    await db.refresh(note)
    return _note_to_response(note, officer)


@router.put("/notes/{note_id}", response_model=NoteResponse)
async def update_note(
    note_id: int,
    body: NoteUpdate,
    db: AsyncSession = Depends(get_db),
    officer: Officer = Depends(require_officer),
):
    """Edit a note. Only the author may edit their own note."""
    note = (await db.execute(select(FIRNote).where(FIRNote.id == note_id))).scalar_one_or_none()
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    if note.officer_id != officer.id:
        raise HTTPException(status_code=403, detail="You can only edit your own notes")

    note.text = body.text.strip()
    await db.commit()
    await db.refresh(note)
    return _note_to_response(note, officer)


@router.delete("/notes/{note_id}")
async def delete_note(
    note_id: int,
    db: AsyncSession = Depends(get_db),
    officer: Officer = Depends(require_officer),
):
    """Delete a note. Allowed for the author or an admin."""
    note = (await db.execute(select(FIRNote).where(FIRNote.id == note_id))).scalar_one_or_none()
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    if note.officer_id != officer.id and not officer.is_admin:
        raise HTTPException(status_code=403, detail="Only the author or an admin can delete this note")

    await db.delete(note)
    await db.commit()
    return {"deleted": True, "note_id": note_id}


# ──────────────────────── Bulk Actions ────────────────────────

@router.post("/bulk-action", response_model=BulkActionResponse)
async def bulk_action(
    body: BulkActionRequest,
    db: AsyncSession = Depends(get_db),
    officer: Officer = Depends(require_officer),
):
    """Apply an action to multiple FIRs at once.

    Supported actions:
      - set_status (requires `status`)
      - add_tag / remove_tag (requires `tag`)
      - delete (admin only)
    """
    action = body.action
    errors: List[str] = []
    affected = 0

    # Load targeted FIRs
    result = await db.execute(select(FIR).where(FIR.id.in_(body.fir_ids)))
    firs = {f.id: f for f in result.scalars().all()}
    missing = [fid for fid in body.fir_ids if fid not in firs]
    for fid in missing:
        errors.append(f"FIR {fid} not found")

    if action == "set_status":
        if body.status not in VALID_STATUSES:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid status. Must be one of: {', '.join(sorted(VALID_STATUSES))}",
            )
        for fir in firs.values():
            old = fir.status
            if old == body.status:
                continue
            fir.status = body.status
            await CaseEventService.log_event(
                db, fir_id=fir.id, event_type="status_changed",
                description=f"{officer.name} changed status: {old or 'new'} -> {body.status}",
                officer_id=officer.id,
                metadata={"old": old, "new": body.status}, commit=False,
            )
            affected += 1

    elif action in ("add_tag", "remove_tag"):
        if not body.tag or not body.tag.strip():
            raise HTTPException(status_code=400, detail="A `tag` is required for tag actions")
        tag = body.tag.strip().lower()
        for fir in firs.values():
            tags = list(fir.tags or [])
            if action == "add_tag" and tag not in tags:
                tags.append(tag)
            elif action == "remove_tag" and tag in tags:
                tags.remove(tag)
            else:
                continue
            fir.tags = tags
            await CaseEventService.log_event(
                db, fir_id=fir.id, event_type="tagged",
                description=f"{officer.name} {'added' if action == 'add_tag' else 'removed'} tag '{tag}'",
                officer_id=officer.id, metadata={"tag": tag, "action": action}, commit=False,
            )
            affected += 1

    elif action == "delete":
        if not officer.is_admin:
            raise HTTPException(status_code=403, detail="Only admins can bulk delete FIRs")
        for fir in firs.values():
            await db.delete(fir)
            affected += 1

    else:
        raise HTTPException(
            status_code=400,
            detail="Unknown action. Use set_status, add_tag, remove_tag, or delete.",
        )

    await db.commit()
    return BulkActionResponse(
        action=action,
        requested=len(body.fir_ids),
        affected=affected,
        skipped=len(body.fir_ids) - affected - len(missing),
        errors=errors,
    )


# ──────────────────────── Timeline ────────────────────────

@router.get("/{fir_id}/timeline", response_model=List[CaseEventResponse])
async def get_timeline(
    fir_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Get the chronological event timeline for a FIR case.

    If no events exist yet (e.g. an older FIR created before timelines were
    introduced), a synthetic 'created' event is derived from the FIR record.
    """
    events = await CaseEventService.get_timeline(db, fir_id)
    if events:
        return events

    fir = (await db.execute(select(FIR).where(FIR.id == fir_id))).scalar_one_or_none()
    if not fir:
        raise HTTPException(status_code=404, detail="FIR not found")

    return [
        CaseEventResponse(
            id=0,
            fir_id=fir.id,
            event_type="created",
            description="FIR registered in the system",
            event_metadata={"crime_type": fir.crime_type, "severity": fir.severity},
            created_at=fir.created_at,
        )
    ]


# ──────────────────────── Notifications ────────────────────────

@router.get("/notifications", response_model=List[NotificationResponse])
async def list_notifications(
    unread_only: bool = Query(False),
    limit: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
    officer: Officer = Depends(require_officer),
):
    """List the current officer's notifications."""
    return await NotificationService.list_for_officer(
        db, officer.id, unread_only=unread_only, limit=limit
    )


@router.get("/notifications/unread-count")
async def notifications_unread_count(
    db: AsyncSession = Depends(get_db),
    officer: Officer = Depends(require_officer),
):
    """Get the count of unread notifications for the badge/bell UI."""
    count = await NotificationService.unread_count(db, officer.id)
    return {"unread": count}


@router.post("/notifications/{notification_id}/read")
async def mark_notification_read(
    notification_id: int,
    db: AsyncSession = Depends(get_db),
    officer: Officer = Depends(require_officer),
):
    """Mark a single notification as read."""
    note = (await db.execute(
        select(Notification).where(Notification.id == notification_id)
    )).scalar_one_or_none()
    if not note or note.officer_id != officer.id:
        raise HTTPException(status_code=404, detail="Notification not found")
    note.is_read = True
    await db.commit()
    return {"id": notification_id, "is_read": True}


@router.post("/notifications/read-all")
async def mark_all_notifications_read(
    db: AsyncSession = Depends(get_db),
    officer: Officer = Depends(require_officer),
):
    """Mark all of the current officer's notifications as read."""
    await db.execute(
        update(Notification)
        .where((Notification.officer_id == officer.id) & (Notification.is_read == False))  # noqa: E712
        .values(is_read=True)
    )
    await db.commit()
    return {"marked_read": True}
