"""
Legal Assistant Router
----------------------
Endpoints for AI-powered legal guidance using the custom
FirAI Engine and the built-in IPC/BNS knowledge base.

Features:
  - Legal Q&A (RAG-powered semantic search)
  - IPC ↔ BNS cross-mapping
  - Punishment calculator
  - Section reference lookup
"""

from typing import Optional, List
from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from database import get_db
from models.fir import FIR
from models.officer import Officer
from schemas.fir import LegalQueryRequest, LegalResponse
from services import firai_engine
from services.legal_kb import lookup_section, get_all_sections, lookup_sections_batch
from routers.auth import require_officer

router = APIRouter(prefix="/api/legal", tags=["Legal Assistant"])


# ─────────────────── Schemas ───────────────────

class SectionInput(BaseModel):
    act: str
    section: str

class PunishmentRequest(BaseModel):
    sections: List[SectionInput]


# ─────────────────── Legal Q&A ───────────────────

@router.post("/query", response_model=LegalResponse)
async def legal_query(
    request: LegalQueryRequest,
    db: AsyncSession = Depends(get_db),
    officer: Officer = Depends(require_officer)
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

    response = await firai_engine.legal_query(request.question, context)

    return LegalResponse(
        answer=response.get("answer", "No answer available"),
        relevant_sections=response.get("relevant_sections", []),
        source_firs=source_firs
    )


# ─────────────────── Section Lookup ───────────────────

@router.get("/sections")
async def list_legal_sections(
    act: Optional[str] = Query(None, description="Filter by act (IPC or BNS)"),
    officer: Officer = Depends(require_officer)
):
    """Get all legal sections from the knowledge base."""
    return get_all_sections(act)


@router.get("/sections/{act}/{section}")
async def get_section_detail(act: str, section: str, officer: Officer = Depends(require_officer)):
    """Look up a specific legal section."""
    return lookup_section(act, section)


@router.post("/sections/lookup")
async def lookup_fir_sections(acts: list, officer: Officer = Depends(require_officer)):
    """Look up all sections for a given FIR's acts list."""
    return lookup_sections_batch(acts)


# ─────────────────── IPC ↔ BNS Cross-Mapping ───────────────────

@router.get("/equivalent/{act}/{section}")
async def get_equivalent_section(
    act: str, section: str,
    officer: Officer = Depends(require_officer)
):
    """
    Get the equivalent section in the other code.
    IPC → BNS or BNS → IPC.
    Also returns full details of the equivalent section from the corpus.
    """
    from ai_engine.data.ipc_bns_map import get_equivalent

    mapping = get_equivalent(act, section)

    # If found, also fetch full details of the equivalent section
    if mapping["found"]:
        details = lookup_section(mapping["equivalent_act"], mapping["equivalent_section"])
        mapping["equivalent_details"] = details

    return mapping


@router.post("/equivalent/batch")
async def get_batch_equivalents(
    sections: List[SectionInput],
    officer: Officer = Depends(require_officer)
):
    """
    Get IPC↔BNS equivalents for a list of sections.
    Useful for mapping all sections in an FIR at once.
    """
    from ai_engine.data.ipc_bns_map import get_equivalent

    results = []
    for s in sections:
        mapping = get_equivalent(s.act, s.section)
        if mapping["found"]:
            mapping["equivalent_details"] = lookup_section(
                mapping["equivalent_act"], mapping["equivalent_section"]
            )
        results.append(mapping)
    return results


# ─────────────────── Punishment Calculator ───────────────────

@router.post("/punishment-calc")
async def calculate_punishment(
    request: PunishmentRequest,
    officer: Officer = Depends(require_officer)
):
    """
    Given a list of legal sections, return structured punishment
    breakdown including min/max, bail status, cognizable status.
    """
    from ai_engine.data.legal_corpus import LEGAL_CORPUS

    results = []
    max_severity_rank = 0
    severity_order = {"low": 1, "medium": 2, "high": 3, "critical": 4}

    for s in request.sections:
        # Search in corpus
        match = None
        base_section = s.section.split("(")[0]
        for entry in LEGAL_CORPUS:
            if entry["section"] == s.section or entry["section"] == base_section:
                act_upper = s.act.upper()
                entry_act_upper = entry["act"].upper()
                if act_upper in entry_act_upper or entry_act_upper in act_upper:
                    match = entry
                    break

        if match:
            sev_rank = severity_order.get(match.get("severity", "low"), 0)
            max_severity_rank = max(max_severity_rank, sev_rank)

            results.append({
                "act": match["act"],
                "section": match["section"],
                "title": match.get("title", ""),
                "punishment": match.get("punishment", "Not available"),
                "bailable": match.get("bailable"),
                "cognizable": match.get("cognizable"),
                "severity": match.get("severity", "unknown"),
                "crime_type": match.get("crime_type", "unknown"),
                "found": True,
            })
        else:
            # Try legal_kb as fallback
            kb_result = lookup_section(s.act, s.section)
            results.append({
                "act": s.act,
                "section": s.section,
                "title": kb_result.get("description", ""),
                "punishment": kb_result.get("punishment", "Not available"),
                "bailable": kb_result.get("bailable"),
                "cognizable": kb_result.get("cognizable"),
                "severity": "unknown",
                "crime_type": kb_result.get("offense_type", "unknown"),
                "found": "Section details not found" not in kb_result.get("description", ""),
            })

    # Overall assessment
    severity_labels = {1: "low", 2: "medium", 3: "high", 4: "critical"}
    overall_severity = severity_labels.get(max_severity_rank, "unknown")
    any_non_bailable = any(r.get("bailable") is False for r in results)

    return {
        "sections": results,
        "summary": {
            "total_sections": len(results),
            "sections_found": sum(1 for r in results if r["found"]),
            "overall_severity": overall_severity,
            "any_non_bailable": any_non_bailable,
            "all_cognizable": all(r.get("cognizable", False) for r in results if r["found"]),
        }
    }
