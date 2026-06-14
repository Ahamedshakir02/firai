"""
Case Collaboration Schemas
--------------------------
Request/response models for notes, bulk actions, timeline, and notifications.
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


# ──────────────────────── Notes ────────────────────────

class NoteCreate(BaseModel):
    text: str = Field(..., min_length=1, max_length=5000, description="Note text")


class NoteUpdate(BaseModel):
    text: str = Field(..., min_length=1, max_length=5000)


class NoteResponse(BaseModel):
    id: int
    fir_id: int
    officer_id: Optional[int] = None
    author_name: Optional[str] = None
    text: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    can_edit: bool = False  # True if requesting officer authored it (or is admin)

    class Config:
        from_attributes = True


# ──────────────────────── Bulk Actions ────────────────────────

class BulkActionRequest(BaseModel):
    fir_ids: List[int] = Field(..., min_length=1, description="FIR IDs to act on")
    action: str = Field(..., description="set_status | add_tag | remove_tag | delete")
    # Action payload
    status: Optional[str] = Field(None, description="For set_status")
    tag: Optional[str] = Field(None, description="For add_tag / remove_tag")


class BulkActionResponse(BaseModel):
    action: str
    requested: int
    affected: int
    skipped: int = 0
    errors: List[str] = []


# ──────────────────────── Timeline ────────────────────────

class CaseEventResponse(BaseModel):
    id: int
    fir_id: int
    officer_id: Optional[int] = None
    event_type: str
    description: Optional[str] = None
    event_metadata: Optional[dict] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# ──────────────────────── Notifications ────────────────────────

class NotificationResponse(BaseModel):
    id: int
    notification_type: str
    title: str
    message: Optional[str] = None
    related_fir_id: Optional[int] = None
    is_read: bool = False
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True
