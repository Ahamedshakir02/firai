"""
MO Patterns Router
------------------
Endpoints for Modus Operandi pattern detection across FIR narratives.
"""

from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from database import get_db
from models.fir import FIR, MOPattern
from models.officer import Officer
from schemas.fir import MOPatternResponse
from services import mo_detector
from routers.auth import require_officer

router = APIRouter(prefix="/api/mo", tags=["MO Patterns"])


@router.get("/patterns", response_model=List[MOPatternResponse])
async def list_mo_patterns(
    db: AsyncSession = Depends(get_db),
    officer: Officer = Depends(require_officer)
):
    """List all detected MO patterns."""
    result = await db.execute(select(MOPattern).order_by(MOPattern.occurrence_count.desc()))
    return result.scalars().all()


@router.post("/detect", response_model=List[MOPatternResponse])
async def detect_mo_patterns(
    db: AsyncSession = Depends(get_db),
    officer: Officer = Depends(require_officer)
):
    """
    Run MO pattern detection on all FIR narratives in the database.
    Analyzes narratives to find recurring crime methods.
    """
    # Get all FIRs with narratives
    result = await db.execute(select(FIR).where(FIR.narrative.isnot(None)))
    firs = result.scalars().all()

    if not firs:
        return []

    narratives = [{"id": f.id, "narrative": f.narrative, "crime_type": f.crime_type} for f in firs]

    # Detect patterns
    patterns = await mo_detector.detect_patterns_from_narratives(narratives)

    # Clear existing patterns before saving new ones (prevents duplicates)
    from sqlalchemy import delete
    await db.execute(delete(MOPattern))
    await db.flush()

    # Save detected patterns to DB
    saved_patterns = []
    for p in patterns:
        mo = MOPattern(
            pattern_name=p.get("pattern_name", "Unknown"),
            description=p.get("description"),
            crime_type=p.get("crime_type"),
            occurrence_count=p.get("occurrence_count", 0),
            linked_fir_ids=p.get("linked_fir_ids", []),
        )
        db.add(mo)
        await db.flush()
        saved_patterns.append(mo)

    await db.commit()

    return saved_patterns
