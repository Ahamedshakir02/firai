"""
Dashboard Router
----------------
Endpoints for dashboard statistics and metrics.
All derived from FIR narratives and their AI classifications.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from collections import Counter

from database import get_db
from models.fir import FIR
from models.officer import Officer
from schemas.fir import DashboardStats, FIRListItem
from routers.auth import require_officer

router = APIRouter(prefix="/api/dashboard", tags=["Dashboard"])


@router.get("/stats", response_model=DashboardStats)
async def get_dashboard_stats(
    db: AsyncSession = Depends(get_db),
    officer: Officer = Depends(require_officer)
):
    """Get dashboard overview statistics."""

    # Total FIRs
    total_result = await db.execute(select(func.count(FIR.id)))
    total_firs = total_result.scalar() or 0

    # Crime type breakdown
    crime_result = await db.execute(
        select(FIR.crime_type, func.count(FIR.id))
        .where(FIR.crime_type.isnot(None))
        .group_by(FIR.crime_type)
    )
    crime_type_breakdown = {row[0]: row[1] for row in crime_result.all()}

    # Severity breakdown
    severity_result = await db.execute(
        select(FIR.severity, func.count(FIR.id))
        .where(FIR.severity.isnot(None))
        .group_by(FIR.severity)
    )
    severity_breakdown = {row[0]: row[1] for row in severity_result.all()}

    # Recent FIRs (last 10)
    recent_result = await db.execute(
        select(FIR)
        .order_by(FIR.created_at.desc())
        .limit(10)
    )
    recent_firs = recent_result.scalars().all()

    # Monthly trend (by FIR date)
    monthly_result = await db.execute(
        select(
            func.extract('month', FIR.fir_date).label('month'),
            func.extract('year', FIR.fir_date).label('year'),
            func.count(FIR.id)
        )
        .where(FIR.fir_date.isnot(None))
        .group_by('year', 'month')
        .order_by('year', 'month')
    )
    monthly_trend = {}
    for row in monthly_result.all():
        if row[0] and row[1]:
            key = f"{int(row[1])}-{int(row[0]):02d}"
            monthly_trend[key] = row[2]

    return DashboardStats(
        total_firs=total_firs,
        crime_type_breakdown=crime_type_breakdown,
        severity_breakdown=severity_breakdown,
        recent_firs=recent_firs,
        monthly_trend=monthly_trend
    )
