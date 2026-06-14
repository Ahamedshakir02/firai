"""
FIR Router
----------
Endpoints for FIR management, analysis, and similarity search.
Supports bulk upload of previous FIRs for preprocessing.
Includes duplicate detection and FIR download.
"""

import os
import json
import mimetypes
import tempfile
import numpy as np
from typing import List, Optional
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, Query
from fastapi.responses import JSONResponse, FileResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from datetime import datetime

from database import get_db
from models.fir import FIR, Accused
from models.officer import Officer
from schemas.fir import (
    NarrativeAnalyzeRequest, FIRListItem, FIRDetail,
    SimilarFIR, AccusedMatch, AnalysisResult, BulkUploadResponse
)
from services import fir_processor
from services import firai_engine
from services.case_service import CaseEventService
from services.fir_processor import generate_fir_filename
from services.embedding_engine import embedding_engine
from routers.auth import require_officer

# All endpoints in this router require a valid JWT token
router = APIRouter(prefix="/api/firs", tags=["FIRs"], dependencies=[Depends(require_officer)])

# Accepted upload formats: PDF plus scanned-image FIRs (OCR'd directly).
ALLOWED_UPLOAD_EXTS = {".pdf"} | set(fir_processor.IMAGE_EXTENSIONS)


def _upload_ext(filename: Optional[str]) -> str:
    """Lower-cased extension of an uploaded filename, or '' if none."""
    return os.path.splitext(filename or "")[1].lower()


# ──────────────────────── Duplicate Detection ────────────────────────

async def _find_duplicate(db: AsyncSession, fir_number: Optional[str] = None,
                          narrative: Optional[str] = None) -> Optional[FIR]:
    """
    Check if a FIR already exists in the database.
    Matches by fir_number first (exact match), then by narrative similarity.
    Returns the existing FIR if found, None otherwise.
    """
    if fir_number and fir_number.strip():
        result = await db.execute(
            select(FIR).where(FIR.fir_number == fir_number.strip())
        )
        existing = result.scalar_one_or_none()
        if existing:
            return existing

    # Check for near-identical narratives (>= 95% similarity)
    if narrative and narrative.strip():
        query_emb = embedding_engine.encode_narrative(narrative).reshape(1, -1)
        result = await db.execute(
            select(FIR).where(FIR.embedding_vector.isnot(None))
        )
        all_firs = result.scalars().all()
        for fir in all_firs:
            stored_emb = np.frombuffer(fir.embedding_vector, dtype=np.float32).reshape(1, -1)
            sim = float(np.dot(query_emb, stored_emb.T)[0][0])
            if sim >= 0.95:
                return fir

    return None


# ──────────────────────── List & Get ────────────────────────

@router.get("")
async def list_firs(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    crime_type: Optional[str] = None,
    police_station: Optional[str] = Query(None, max_length=100),
    severity: Optional[str] = None,
    search: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """List all FIRs with optional filtering, sorted by FIR case number.

    Returns paginated results with total count for UI pagination.
    """
    # Build base query for filtering
    base_query = select(FIR)

    if crime_type:
        base_query = base_query.where(FIR.crime_type == crime_type)
    if police_station:
        base_query = base_query.where(FIR.police_station.ilike(f"%{police_station}%"))
    if severity:
        base_query = base_query.where(FIR.severity == severity)
    if search:
        base_query = base_query.where(FIR.narrative.icontains(search))

    # Get total count (before pagination)
    count_result = await db.execute(
        select(func.count(FIR.id)).select_from(FIR).where(base_query.whereclause)
    )
    total_count = count_result.scalar() or 0

    # Apply pagination and ordering
    query = base_query.offset(skip).limit(limit).order_by(
        FIR.fir_number.asc().nulls_last(),
        FIR.created_at.desc()
    )

    result = await db.execute(query)
    firs = result.scalars().all()

    return {
        "total": total_count,
        "skip": skip,
        "limit": limit,
        "items": [FIRListItem.model_validate(fir) for fir in firs],
    }


@router.get("/export/all")
async def export_all_firs(db: AsyncSession = Depends(get_db)):
    """Export all FIRs as a JSON array for backup/download."""
    result = await db.execute(select(FIR).order_by(FIR.fir_number.asc().nulls_last()))
    firs = result.scalars().all()

    export_data = []
    for fir in firs:
        accused_result = await db.execute(select(Accused).where(Accused.fir_id == fir.id))
        accused_list = accused_result.scalars().all()

        export_data.append({
            "id": fir.id,
            "fir_number": fir.fir_number,
            "fir_date": str(fir.fir_date) if fir.fir_date else None,
            "district": fir.district,
            "police_station": fir.police_station,
            "place": fir.place,
            "narrative": fir.narrative,
            "crime_type": fir.crime_type,
            "severity": fir.severity,
            "summary_en": fir.summary_en,
            "acts": fir.acts,
            "accused": [
                {"name": a.name, "father_name": a.father_name}
                for a in accused_list
            ],
        })

    return JSONResponse(
        content=export_data,
        headers={
            "Content-Disposition": 'attachment; filename="all_firs_export.json"'
        }
    )


@router.get("/{fir_id}", response_model=FIRDetail)
async def get_fir(fir_id: int, db: AsyncSession = Depends(get_db)):
    """Get a specific FIR with all details."""
    result = await db.execute(select(FIR).where(FIR.id == fir_id))
    fir = result.scalar_one_or_none()

    if not fir:
        raise HTTPException(status_code=404, detail="FIR not found")

    # Load accused
    accused_result = await db.execute(select(Accused).where(Accused.fir_id == fir_id))
    accused_list = accused_result.scalars().all()

    # Build response manually to include accused
    fir_dict = {
        "id": fir.id, "file_name": fir.file_name, "fir_number": fir.fir_number,
        "fir_date": fir.fir_date, "district": fir.district,
        "police_station": fir.police_station, "place": fir.place,
        "narrative": fir.narrative, "narrative_en": fir.narrative_en,
        "narrative_ml": fir.narrative_ml, "full_text": fir.full_text,
        "crime_type": fir.crime_type, "severity": fir.severity,
        "summary_en": fir.summary_en,
        "recommended_steps": fir.recommended_steps,
        "key_entities": fir.key_entities, "acts": fir.acts,
        "complainant": fir.complainant, "created_at": fir.created_at,
        "accused": [{"id": a.id, "name": a.name, "father_name": a.father_name,
                      "dob": a.dob, "address": a.address} for a in accused_list]
    }
    return fir_dict


# ──────────────────────── Download ────────────────────────

@router.get("/{fir_id}/download")
async def download_fir(fir_id: int, db: AsyncSession = Depends(get_db)):
    """
    Download a FIR. Returns the actual PDF if available, 
    otherwise falls back to a structured JSON file.
    """
    # Look up the FIR to get its proper file_name
    result_fir = await db.execute(select(FIR).where(FIR.id == fir_id))
    fir_record = result_fir.scalar_one_or_none()

    pdf_dir = os.path.join(os.path.dirname(__file__), "..", "data", "raw_pdfs")

    # Try the stored file_name first (an image FIR keeps its own extension; a
    # legacy .json name maps to its .pdf sibling), then the legacy id-based name.
    candidates = []
    if fir_record and fir_record.file_name:
        import re
        candidates.append(re.sub(r'\.json$', '.pdf', fir_record.file_name, flags=re.IGNORECASE))
    candidates.append(f"{fir_id}.pdf")

    for candidate in candidates:
        doc_path = os.path.join(pdf_dir, candidate)
        if os.path.exists(doc_path):
            media_type = mimetypes.guess_type(candidate)[0] or "application/octet-stream"
            return FileResponse(
                path=doc_path,
                filename=candidate,
                media_type=media_type,
            )

    # Fallback to JSON if PDF is not available
    result = await db.execute(select(FIR).where(FIR.id == fir_id))
    fir = result.scalar_one_or_none()

    if not fir:
        raise HTTPException(status_code=404, detail="FIR not found")

    # Load accused
    accused_result = await db.execute(select(Accused).where(Accused.fir_id == fir_id))
    accused_list = accused_result.scalars().all()

    fir_data = {
        "fir_number": fir.fir_number,
        "fir_date": str(fir.fir_date) if fir.fir_date else None,
        "district": fir.district,
        "police_station": fir.police_station,
        "place": fir.place,
        "narrative": fir.narrative,
        "narrative_en": fir.narrative_en,
        "full_text": fir.full_text,
        "crime_type": fir.crime_type,
        "severity": fir.severity,
        "summary_en": fir.summary_en,
        "recommended_steps": fir.recommended_steps,
        "key_entities": fir.key_entities,
        "acts": fir.acts,
        "complainant": fir.complainant,
        "accused": [
            {"name": a.name, "father_name": a.father_name,
             "dob": a.dob, "address": a.address}
            for a in accused_list
        ],
    }

    filename = fir.fir_number.replace("/", "-") if fir.fir_number else f"FIR-{fir.id}"
    return JSONResponse(
        content=fir_data,
        headers={
            "Content-Disposition": f'attachment; filename="{filename}.json"'
        }
    )




# ──────────────────────── Upload & Analyze ────────────────────────

@router.post("/upload-pdf", response_model=AnalysisResult)
async def upload_fir_pdf(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db)
):
    """
    Upload a single FIR document (PDF or scanned image), process it,
    extract the narrative, analyze with AI, and store in the database.
    Detects duplicates by FIR number or narrative similarity.
    """
    ext = _upload_ext(file.filename)
    if ext not in ALLOWED_UPLOAD_EXTS:
        raise HTTPException(
            status_code=400,
            detail="Only PDF or image files (PNG, JPG, JPEG, TIFF, BMP, WEBP) are accepted",
        )

    # Save temp file (preserve original extension so OCR dispatches correctly)
    with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as temp:
        content = await file.read()
        temp.write(content)
        temp_path = temp.name

    try:
        # Process document → extract narrative and metadata (PDF or image)
        processed = fir_processor.process_fir_document(temp_path, file.filename)
        narrative = processed["narrative"]
        fir_number = processed.get("fir_number")

        # Analyze narrative with FirAI Engine (custom AI)
        # Pass acts and full_text so classification uses IPC/BNS sections
        analysis = await firai_engine.analyze_narrative(
            narrative,
            acts=processed.get("acts", []),
            full_text=processed.get("full_text", "")
        )

        # Check for duplicates
        existing = await _find_duplicate(db, fir_number=fir_number, narrative=narrative)
        if existing:
            # Return analysis with duplicate flag — don't add to DB
            similar = await _find_similar_in_db(
                narrative, db, exclude_id=existing.id,
                crime_type=analysis.get("crime_type"),
                accused_list=processed.get("accused", [])
            )
            return AnalysisResult(
                crime_type=analysis.get("crime_type"),
                severity=analysis.get("severity"),
                narrative=narrative,
                fir_number=fir_number,
                summary_en=analysis.get("summary_en"),
                ipc_sections=analysis.get("ipc_sections"),
                recommended_steps=analysis.get("recommended_steps"),
                key_entities=analysis.get("key_entities"),
                similar_firs=similar,
                is_duplicate=True,
                duplicate_of_id=existing.id,
            )

        # Generate proper FIR-based filename (preserve original extension)
        proper_filename = generate_fir_filename(
            fir_number=fir_number,
            police_station=processed.get("police_station"),
            fallback_name=file.filename,
            extension=ext,
        )

        # Create FIR record
        fir = FIR(
            file_name=proper_filename,
            fir_number=fir_number,
            narrative=narrative,
            full_text=processed["full_text"],
            fir_date=_parse_date(processed.get("fir_date")),
            district=processed.get("district"),
            police_station=processed.get("police_station"),
            place=processed.get("place"),
            acts=processed.get("acts"),
            complainant=processed.get("complainant"),
            crime_type=analysis.get("crime_type"),
            severity=analysis.get("severity"),
            summary_en=analysis.get("summary_en"),
            recommended_steps=analysis.get("recommended_steps"),
            key_entities=analysis.get("key_entities"),
        )

        # Generate embedding
        embedding = embedding_engine.encode_narrative(narrative)
        fir.embedding_vector = embedding.tobytes()

        db.add(fir)
        await db.flush()

        # Add accused
        for acc in processed.get("accused", []):
            accused = Accused(fir_id=fir.id, name=acc.get("name"),
                              father_name=acc.get("father_name"),
                              dob=acc.get("dob"), address=acc.get("address"))
            db.add(accused)

        await db.commit()

        # Record the case-creation event for the timeline
        await CaseEventService.log_event(
            db, fir_id=fir.id, event_type="created",
            description="FIR uploaded and analyzed",
            metadata={"crime_type": analysis.get("crime_type"), "severity": analysis.get("severity")},
        )

        # Save PDF to raw_pdfs folder with proper FIR-based name
        import shutil
        pdf_dir = os.path.join(os.path.dirname(__file__), "..", "data", "raw_pdfs")
        os.makedirs(pdf_dir, exist_ok=True)
        pdf_dest = os.path.join(pdf_dir, proper_filename)
        
        try:
            shutil.copy2(temp_path, pdf_dest)
        except Exception as e:
            print(f"[Upload] Warning: Could not copy PDF to permanent storage: {e}")

        # Find similar FIRs
        similar = await _find_similar_in_db(
            narrative, db, exclude_id=fir.id,
            crime_type=analysis.get("crime_type"),
            accused_list=processed.get("accused", [])
        )

        return AnalysisResult(
            crime_type=analysis.get("crime_type"),
            severity=analysis.get("severity"),
            narrative=narrative,
            fir_number=fir_number,
            summary_en=analysis.get("summary_en"),
            ipc_sections=analysis.get("ipc_sections"),
            recommended_steps=analysis.get("recommended_steps"),
            key_entities=analysis.get("key_entities"),
            similar_firs=similar,
            is_duplicate=False,
        )

    finally:
        os.unlink(temp_path)


@router.post("/analyze-text", response_model=AnalysisResult)
async def analyze_narrative_text(
    request: NarrativeAnalyzeRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Analyze a pasted FIR narrative text (Malayalam or English).
    Does NOT save to database — just returns analysis.
    Also checks if this narrative already exists in the database.
    """
    analysis = await firai_engine.analyze_narrative(request.narrative)
    similar = await _find_similar_in_db(
        request.narrative, db, top_k=request.top_k,
        crime_type=analysis.get("crime_type")
    )

    # Check for duplicates
    existing = await _find_duplicate(db, narrative=request.narrative)

    return AnalysisResult(
        crime_type=analysis.get("crime_type"),
        severity=analysis.get("severity"),
        narrative=request.narrative,
        fir_number=analysis.get("fir_number"),
        summary_en=analysis.get("summary_en"),
        ipc_sections=analysis.get("ipc_sections"),
        recommended_steps=analysis.get("recommended_steps"),
        key_entities=analysis.get("key_entities"),
        similar_firs=similar,
        is_duplicate=existing is not None,
        duplicate_of_id=existing.id if existing else None,
    )


@router.post("/analyze-and-save", response_model=FIRDetail)
async def analyze_and_save_narrative(
    request: NarrativeAnalyzeRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Analyze a narrative and save it as a new FIR in the database.
    Checks for duplicates first — returns existing FIR if found.
    """
    analysis = await firai_engine.analyze_narrative(request.narrative)

    # Check for duplicates before saving
    existing = await _find_duplicate(db, narrative=request.narrative)
    if existing:
        # Return the existing FIR instead of creating a duplicate
        accused_result = await db.execute(select(Accused).where(Accused.fir_id == existing.id))
        accused_list = accused_result.scalars().all()
        fir_dict = {
            "id": existing.id, "file_name": existing.file_name,
            "fir_number": existing.fir_number, "fir_date": existing.fir_date,
            "district": existing.district, "police_station": existing.police_station,
            "place": existing.place, "narrative": existing.narrative,
            "narrative_en": existing.narrative_en, "narrative_ml": existing.narrative_ml,
            "full_text": existing.full_text, "crime_type": existing.crime_type,
            "severity": existing.severity, "summary_en": existing.summary_en,
            "recommended_steps": existing.recommended_steps,
            "key_entities": existing.key_entities, "acts": existing.acts,
            "complainant": existing.complainant, "created_at": existing.created_at,
            "accused": [{"id": a.id, "name": a.name, "father_name": a.father_name,
                          "dob": a.dob, "address": a.address} for a in accused_list]
        }
        return fir_dict

    fir = FIR(
        narrative=request.narrative,
        fir_number=analysis.get("fir_number"),
        crime_type=analysis.get("crime_type"),
        severity=analysis.get("severity"),
        summary_en=analysis.get("summary_en"),
        recommended_steps=analysis.get("recommended_steps"),
        key_entities=analysis.get("key_entities"),
        acts=analysis.get("ipc_sections"),
    )

    embedding = embedding_engine.encode_narrative(request.narrative)
    fir.embedding_vector = embedding.tobytes()

    db.add(fir)
    await db.commit()
    await db.refresh(fir)

    return fir


# ──────────────────────── Bulk Upload ────────────────────────

@router.post("/bulk-upload", response_model=BulkUploadResponse)
async def bulk_upload_firs(
    files: List[UploadFile] = File(...),
    db: AsyncSession = Depends(get_db)
):
    """
    Bulk upload multiple FIR PDFs.
    Processes each one: extract narrative → analyze → store in DB.
    Skips duplicates (same FIR number or near-identical narrative).
    """
    total = len(files)
    processed_count = 0
    skipped_duplicates = 0
    errors = []
    duplicates = []

    for file in files:
        ext = _upload_ext(file.filename)
        if ext not in ALLOWED_UPLOAD_EXTS:
            errors.append(f"{file.filename}: Not a PDF or supported image file")
            continue

        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as temp:
                content = await file.read()
                temp.write(content)
                temp_path = temp.name

            # Process document (PDF or image)
            processed = fir_processor.process_fir_document(temp_path, file.filename)
            fir_number = processed.get("fir_number")
            narrative = processed["narrative"]

            # Check for duplicates
            existing = await _find_duplicate(db, fir_number=fir_number, narrative=narrative)
            if existing:
                skipped_duplicates += 1
                dup_label = fir_number or file.filename
                duplicates.append(f"{dup_label} (matches existing FIR #{existing.id})")
                os.unlink(temp_path)
                continue

            # Analyze narrative with FirAI Engine (custom AI)
            try:
                analysis = await firai_engine.analyze_narrative(
                    narrative,
                    acts=processed.get("acts", []),
                    full_text=processed.get("full_text", "")
                )
            except Exception:
                analysis = firai_engine._fallback_analysis(
                    narrative,
                    acts=processed.get("acts", []),
                    full_text=processed.get("full_text", "")
                )

            # Generate proper FIR-based filename (preserve original extension)
            proper_filename = generate_fir_filename(
                fir_number=fir_number,
                police_station=processed.get("police_station"),
                fallback_name=file.filename,
                extension=ext,
            )

            # Create FIR record
            fir = FIR(
                file_name=proper_filename,
                fir_number=fir_number,
                narrative=narrative,
                full_text=processed["full_text"],
                fir_date=_parse_date(processed.get("fir_date")),
                district=processed.get("district"),
                police_station=processed.get("police_station"),
                place=processed.get("place"),
                acts=processed.get("acts"),
                complainant=processed.get("complainant"),
                crime_type=analysis.get("crime_type"),
                severity=analysis.get("severity"),
                summary_en=analysis.get("summary_en"),
                recommended_steps=analysis.get("recommended_steps"),
                key_entities=analysis.get("key_entities"),
            )

            embedding = embedding_engine.encode_narrative(narrative)
            fir.embedding_vector = embedding.tobytes()

            db.add(fir)
            await db.flush()  # Flush to get fir.id before adding accused

            # Add accused — use fir.id now that FIR has been flushed
            for acc in processed.get("accused", []):
                db.add(Accused(fir_id=fir.id, name=acc.get("name"),
                               father_name=acc.get("father_name"),
                               dob=acc.get("dob"),
                               address=acc.get("address")))

            await db.flush()
            processed_count += 1

            os.unlink(temp_path)

        except Exception as e:
            errors.append(f"{file.filename}: {str(e)}")

    await db.commit()

    return BulkUploadResponse(
        total_files=total,
        processed=processed_count,
        failed=total - processed_count - skipped_duplicates,
        skipped_duplicates=skipped_duplicates,
        errors=errors,
        duplicates=duplicates
    )


@router.post("/bulk-upload-json", response_model=BulkUploadResponse)
async def bulk_upload_json(
    files: List[UploadFile] = File(...),
    db: AsyncSession = Depends(get_db)
):
    """
    Bulk upload pre-processed FIR JSON files.
    For importing previously structured FIR data directly.
    Each JSON must have a 'narrative' field.
    Skips duplicates.
    """
    total = len(files)
    processed_count = 0
    skipped_duplicates = 0
    errors = []
    duplicates = []

    for file in files:
        try:
            content = await file.read()
            data = json.loads(content.decode("utf-8"))

            narrative = data.get("narrative", "").strip()
            if not narrative:
                errors.append(f"{file.filename}: No narrative found")
                continue

            # Check for duplicates
            fir_number = data.get("fir_number")
            existing = await _find_duplicate(db, fir_number=fir_number, narrative=narrative)
            if existing:
                skipped_duplicates += 1
                dup_label = fir_number or file.filename
                duplicates.append(f"{dup_label} (matches existing FIR #{existing.id})")
                continue

            # Analyze narrative with FirAI Engine (custom AI)
            try:
                analysis = await firai_engine.analyze_narrative(
                    narrative,
                    acts=data.get("acts", []),
                    full_text=data.get("full_text", "")
                )
            except Exception:
                analysis = firai_engine._fallback_analysis(
                    narrative,
                    acts=data.get("acts", []),
                    full_text=data.get("full_text", "")
                )

            fir = FIR(
                file_name=data.get("file", file.filename),
                fir_number=fir_number,
                narrative=narrative,
                full_text=data.get("full_text"),
                fir_date=_parse_date(data.get("date")),
                place=data.get("place"),
                acts=data.get("acts"),
                complainant=data.get("complainant"),
                crime_type=analysis.get("crime_type"),
                severity=analysis.get("severity"),
                summary_en=analysis.get("summary_en"),
                recommended_steps=analysis.get("recommended_steps"),
                key_entities=analysis.get("key_entities"),
            )

            embedding = embedding_engine.encode_narrative(narrative)
            fir.embedding_vector = embedding.tobytes()

            db.add(fir)
            await db.flush()  # Flush to get fir.id before adding accused

            # Add accused from JSON — use fir.id now that FIR has been flushed
            for acc in data.get("accused", []):
                if acc.get("name"):
                    db.add(Accused(fir_id=fir.id, name=acc["name"],
                                   father_name=acc.get("father_name"),
                                   dob=acc.get("dob"),
                                   address=acc.get("address")))

            await db.flush()
            processed_count += 1

        except Exception as e:
            errors.append(f"{file.filename}: {str(e)}")

    await db.commit()

    return BulkUploadResponse(
        total_files=total,
        processed=processed_count,
        failed=total - processed_count - skipped_duplicates,
        skipped_duplicates=skipped_duplicates,
        errors=errors,
        duplicates=duplicates
    )


# ──────────────────────── Similar FIRs ────────────────────────

@router.get("/{fir_id}/similar", response_model=List[SimilarFIR])
async def get_similar_firs(
    fir_id: int,
    top_k: int = Query(5, ge=1, le=20),
    db: AsyncSession = Depends(get_db)
):
    """Find FIRs similar to a specific FIR using multi-dimensional similarity
    (narrative + crime type + repeat-offender matching)."""
    result = await db.execute(select(FIR).where(FIR.id == fir_id))
    fir = result.scalar_one_or_none()

    if not fir:
        raise HTTPException(status_code=404, detail="FIR not found")

    # Pass the source FIR's crime type and accused so the full multi-dimensional
    # scoring is engaged — not just the narrative dimension.
    acc_result = await db.execute(select(Accused).where(Accused.fir_id == fir.id))
    accused_list = [
        {"name": a.name, "father_name": a.father_name, "dob": a.dob, "address": a.address}
        for a in acc_result.scalars().all()
    ]

    return await _find_similar_in_db(
        fir.narrative, db, top_k=top_k, exclude_id=fir.id,
        crime_type=fir.crime_type, accused_list=accused_list,
    )


# ──────────────────────── Helper Functions ────────────────────────

async def _find_similar_in_db(
    narrative: str, db: AsyncSession, top_k: int = 5,
    exclude_id: int = None, min_score: float = 0.45,
    crime_type: str = None, accused_list: list = None
) -> list:
    """Find similar FIRs using multi-dimensional similarity:
    1. Narrative embedding similarity (cosine)
    2. Crime type matching (same crime = bonus)
    3. Accused name matching (same accused = bonus + disambiguation details)

    Returns results sorted by combined weighted score."""
    from difflib import SequenceMatcher

    # Get all FIRs with embeddings
    query = select(FIR).where(FIR.embedding_vector.isnot(None))
    if exclude_id:
        query = query.where(FIR.id != exclude_id)

    result = await db.execute(query)
    all_firs = result.scalars().all()

    if not all_firs:
        return []

    # Load accused for all candidate FIRs
    accused_by_fir = {}
    for fir in all_firs:
        acc_result = await db.execute(select(Accused).where(Accused.fir_id == fir.id))
        accused_by_fir[fir.id] = acc_result.scalars().all()

    # Encode query narrative
    query_embedding = embedding_engine.encode_narrative(narrative).reshape(1, -1)

    # Normalize accused names for comparison
    def _norm_name(name):
        if not name:
            return ""
        return name.strip().lower().replace(".", "").replace(",", "")

    def _name_similar(n1, n2):
        """Fuzzy name matching — handles slight spelling differences."""
        n1, n2 = _norm_name(n1), _norm_name(n2)
        if not n1 or not n2:
            return False
        if n1 == n2:
            return True
        return SequenceMatcher(None, n1, n2).ratio() >= 0.80

    # Score each candidate FIR
    scored = []
    for fir in all_firs:
        # 1. Narrative similarity (0-1)
        stored_emb = np.frombuffer(fir.embedding_vector, dtype=np.float32).reshape(1, -1)
        narr_sim = float(np.dot(query_embedding, stored_emb.T)[0][0])

        # 2. Crime type match (boolean bonus)
        ct_match = False
        if crime_type and fir.crime_type:
            ct_match = crime_type.lower().strip() == fir.crime_type.lower().strip()

        # 3. Accused matching
        matched_acc = []
        if accused_list:
            fir_accused = accused_by_fir.get(fir.id, [])
            for input_acc in accused_list:
                input_name = input_acc.get("name", "")
                for db_acc in fir_accused:
                    if _name_similar(input_name, db_acc.name):
                        # Determine if likely same person
                        likely_same = False
                        matches_count = 0
                        if input_acc.get("father_name") and db_acc.father_name:
                            if _name_similar(input_acc["father_name"], db_acc.father_name):
                                matches_count += 1
                        if input_acc.get("dob") and db_acc.dob:
                            if input_acc["dob"].strip() == db_acc.dob.strip():
                                matches_count += 1
                        if input_acc.get("address") and db_acc.address:
                            if SequenceMatcher(None, input_acc["address"].lower(), db_acc.address.lower()).ratio() >= 0.6:
                                matches_count += 1
                        # Same person if name matches AND at least 1 other detail matches
                        likely_same = matches_count >= 1

                        matched_acc.append(AccusedMatch(
                            name=input_name,
                            this_fir={
                                "father_name": input_acc.get("father_name"),
                                "dob": input_acc.get("dob"),
                                "address": input_acc.get("address"),
                            },
                            matching_fir={
                                "father_name": db_acc.father_name,
                                "dob": db_acc.dob,
                                "address": db_acc.address,
                            },
                            likely_same_person=likely_same,
                        ))
                        break  # One match per input accused

        # Combined weighted score:
        # 60% narrative similarity + 20% crime type match + 20% accused match
        acc_score = min(len(matched_acc) / max(len(accused_list or []), 1), 1.0)
        combined = (narr_sim * 0.6) + (0.2 if ct_match else 0.0) + (acc_score * 0.2)

        if combined >= min_score or len(matched_acc) > 0:
            scored.append({
                "fir": fir,
                "combined": combined,
                "narr_sim": narr_sim,
                "ct_match": ct_match,
                "matched_accused": matched_acc,
            })

    # Sort by combined score
    scored.sort(key=lambda x: x["combined"], reverse=True)

    return [
        SimilarFIR(
            id=s["fir"].id,
            file_name=s["fir"].file_name,
            fir_number=s["fir"].fir_number,
            crime_type=s["fir"].crime_type,
            severity=s["fir"].severity,
            narrative=s["fir"].narrative[:300] if s["fir"].narrative else None,
            summary_en=s["fir"].summary_en,
            similarity_score=round(s["combined"], 4),
            acts=s["fir"].acts,
            narrative_similarity=round(s["narr_sim"], 4),
            crime_type_match=s["ct_match"],
            accused_match_count=len(s["matched_accused"]),
            matched_accused=s["matched_accused"],
        )
        for s in scored[:top_k]
    ]


def _parse_date(date_str):
    """Parse date string in DD/MM/YYYY or DD-MM-YYYY format."""
    if not date_str:
        return None
    try:
        for fmt in ["%d/%m/%Y", "%d-%m-%Y", "%Y-%m-%d"]:
            try:
                return datetime.strptime(date_str, fmt).date()
            except ValueError:
                continue
    except Exception:
        pass
    print(f"[FirAI] Warning: Unable to parse date string: '{date_str}'")
    return None
