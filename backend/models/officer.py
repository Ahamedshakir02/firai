"""
Officer Model & Registration Request
--------------------------------------
Database models for officer authentication,
profile data, and new officer registration requests.
"""

from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime
from sqlalchemy.sql import func
from database import Base


class Officer(Base):
    __tablename__ = "officers"

    id = Column(Integer, primary_key=True, index=True)
    badge_number = Column(String(50), unique=True, nullable=False, index=True)
    name = Column(String(200), nullable=False)
    rank = Column(String(100))           # SI, ASI, CI, Inspector, etc.
    police_station = Column(String(200))
    district = Column(String(100))
    phone = Column(String(20), nullable=True)
    email = Column(String(200), nullable=True)
    password_hash = Column(String(500), nullable=False)
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class RegistrationRequest(Base):
    __tablename__ = "registration_requests"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    badge_number = Column(String(50), nullable=False)
    rank = Column(String(100))
    police_station = Column(String(200))
    district = Column(String(100))
    phone = Column(String(20), nullable=True)
    email = Column(String(200), nullable=True)

    # Request status: pending, approved, rejected
    status = Column(String(20), default="pending")
    reviewed_by = Column(String(200), nullable=True)   # Admin who reviewed
    reject_reason = Column(Text, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    reviewed_at = Column(DateTime(timezone=True), nullable=True)
