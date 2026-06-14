"""
Case Collaboration Models
-------------------------
Database models for case annotations (notes), case timeline events,
and officer notifications. These power the bulk-actions, annotation,
timeline, and alerting features.
"""

from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base


class FIRNote(Base):
    """An officer's annotation / note attached to a FIR case."""

    __tablename__ = "fir_notes"

    id = Column(Integer, primary_key=True, index=True)

    fir_id = Column(Integer, ForeignKey("firs.id", ondelete="CASCADE"), nullable=False, index=True)
    officer_id = Column(Integer, ForeignKey("officers.id", ondelete="SET NULL"), nullable=True)

    # Cached author name so notes still render if the officer is removed
    author_name = Column(String(200), nullable=True)

    text = Column(Text, nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class CaseEvent(Base):
    """A timeline event in the life of a FIR case.

    event_type examples: created, status_changed, note_added, analyzed,
    similar_found, pattern_matched, tagged, bulk_updated.
    """

    __tablename__ = "case_events"

    id = Column(Integer, primary_key=True, index=True)

    fir_id = Column(Integer, ForeignKey("firs.id", ondelete="CASCADE"), nullable=False, index=True)
    officer_id = Column(Integer, ForeignKey("officers.id", ondelete="SET NULL"), nullable=True)

    event_type = Column(String(50), nullable=False)
    description = Column(Text, nullable=True)

    # Free-form structured context (old/new status, matched fir ids, etc.)
    event_metadata = Column(JSON, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)


class Notification(Base):
    """An in-app alert delivered to an officer.

    notification_type examples: pattern_match, similar_case, status_change,
    note_mention, system.
    """

    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)

    officer_id = Column(Integer, ForeignKey("officers.id", ondelete="CASCADE"), nullable=False, index=True)

    notification_type = Column(String(50), nullable=False)
    title = Column(String(200), nullable=False)
    message = Column(Text, nullable=True)

    # Optional link back to a FIR case
    related_fir_id = Column(Integer, ForeignKey("firs.id", ondelete="SET NULL"), nullable=True)

    is_read = Column(Boolean, default=False, index=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
