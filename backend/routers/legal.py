"""
Legal Assistant Router
----------------------
Endpoints for AI-powered legal guidance using Gemini
and the built-in IPC/BNS knowledge base.
"""

from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from database import get_db
from models.fir import FIR
from schemas.fir import LegalQueryRequest, LegalResponse
from services import gemini_service
from services.legal_kb import lookup_section, get_all_sections, lookup_sections_batch

router = APIRouter(prefix="/api/legal", tags=["Legal Assistant"])


@router.post("/query", response_model=LegalResponse)
async def legal_query(
    request: LegalQueryRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Ask a legal question. If a FIR ID is provided, the FIR narrative
    is used as context for the answer.
    """
    context = ""
    source_firs = []

    if request.fir_id:
        result = await db.execute(select(FIR).where(FIR.id == request.fir_id))
        fir = result.scalar_one_or_none()
        if fir:
            context = fir.narrative or ""
            source_firs = [{"id": fir.id, "file_name": fir.file_name}]

    response = await gemini_service.legal_query(request.question, context)

    return LegalResponse(
        answer=response.get("answer", "No answer available"),
        relevant_sections=response.get("relevant_sections", []),
        source_firs=source_firs
    )


@router.get("/sections")
async def list_legal_sections(
    act: Optional[str] = Query(None, description="Filter by act (IPC or BNS)")
):
    """Get all legal sections from the knowledge base."""
    return get_all_sections(act)


@router.get("/sections/{act}/{section}")
async def get_section_detail(act: str, section: str):
    """Look up a specific legal section."""
    return lookup_section(act, section)


@router.post("/sections/lookup")
async def lookup_fir_sections(acts: list):
    """Look up all sections for a given FIR's acts list."""
    return lookup_sections_batch(acts)
