from sqlalchemy import Column, Integer, String, Text, Float, Boolean, Date, DateTime, ForeignKey, JSON, LargeBinary
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base


class FIR(Base):
    __tablename__ = "firs"

    id = Column(Integer, primary_key=True, index=True)
    file_name = Column(String(100))
    fir_number = Column(String(50))
    fir_date = Column(Date, nullable=True)
    district = Column(String(100))
    police_station = Column(String(100))
    place = Column(Text)

    # THE CORE: narrative text (can be Malayalam or English or both)
    narrative = Column(Text, nullable=False)
    narrative_en = Column(Text, nullable=True)       # English translation
    narrative_ml = Column(Text, nullable=True)        # Malayalam original (if narrative is English)
    full_text = Column(Text)                          # Full OCR text for reference

    # AI-derived from narrative (populated by FirAI Engine)
    crime_type = Column(String(100))
    severity = Column(String(20))                     # low, medium, high, critical
    risk_score = Column(Float)
    summary_en = Column(Text)                         # AI-generated English summary
    recommended_steps = Column(JSON)                  # Investigation next steps
    key_entities = Column(JSON)                        # Extracted entities from narrative

    # Structured metadata
    acts = Column(JSON)                               # [{act, sections}]
    complainant = Column(JSON)                         # {name, father_name, dob}

    # Case workflow state (used by bulk actions & timeline)
    status = Column(String(30), default="new")        # new, under_investigation, charge_sheeted, closed
    tags = Column(JSON, nullable=True)                 # ["urgent", "repeat_offender", ...]

    # Embedding for narrative similarity
    embedding_vector = Column(LargeBinary, nullable=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    accused = relationship("Accused", back_populates="fir", cascade="all, delete-orphan")


class Accused(Base):
    __tablename__ = "accused"

    id = Column(Integer, primary_key=True, index=True)
    fir_id = Column(Integer, ForeignKey("firs.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(200))
    father_name = Column(String(200), nullable=True)
    dob = Column(String(50), nullable=True)
    address = Column(Text, nullable=True)

    # Relationship
    fir = relationship("FIR", back_populates="accused")


class MOPattern(Base):
    __tablename__ = "mo_patterns"

    id = Column(Integer, primary_key=True, index=True)
    pattern_name = Column(String(200), nullable=False)
    description = Column(Text)
    crime_type = Column(String(100))
    occurrence_count = Column(Integer, default=0)
    linked_fir_ids = Column(JSON)
    first_seen = Column(DateTime(timezone=True))
    last_seen = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class LegalSection(Base):
    __tablename__ = "legal_sections"

    id = Column(Integer, primary_key=True, index=True)
    act_name = Column(String(200), nullable=False)
    section_number = Column(String(50), nullable=False)
    description = Column(Text)
    offense_type = Column(String(100))
    cognizable = Column(Boolean, nullable=True)
    bailable = Column(Boolean, nullable=True)
    punishment = Column(Text, nullable=True)
