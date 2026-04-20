"""
FIR Router
----------
Endpoints for FIR management, analysis, and similarity search.
Supports bulk upload of previous FIRs for preprocessing.
"""

import os
import json
import tempfile
import numpy as np
from typing import List, Optional
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from datetime import datetime

from database import get_db
from models.fir import FIR, Accused
from schemas.fir import (
    NarrativeAnalyzeRequest, FIRListItem, FIRDetail,
    SimilarFIR, AnalysisResult, BulkUploadResponse
)
from services import fir_processor, gemini_service
from services.embedding_engine import embedding_engine

router = APIRouter(prefix="/api/firs", tags=["FIRs"])


@router.get("", response_model=List[FIRListItem])
async def list_firs(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    crime_type: Optional[str] = None,
    severity: Optional[str] = None,
    search: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """List all FIRs with optional filtering, sorted by FIR case number."""
    query = select(FIR).offset(skip).limit(limit).order_by(
        # Sort numerically by the number part of fir_number (e.g. '0017/2025' → 17)
        # NULLs go last; fall back to created_at
        FIR.fir_number.asc().nulls_last(),
        FIR.created_at.desc()
    )

    if crime_type:
        query = query.where(FIR.crime_type == crime_type)
    if severity:
        query = query.where(FIR.severity == severity)
    if search:
        query = query.where(FIR.narrative.icontains(search))

    result = await db.execute(query)
    firs = result.scalars().all()
    return firs


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


@router.post("/upload-pdf", response_model=AnalysisResult)
async def upload_fir_pdf(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db)
):
    """
    Upload a single FIR PDF, process it, extract narrative,
    analyze with AI, and store in database.
    """
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files accepted")

    # Save temp file
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp:
        content = await file.read()
        temp.write(content)
        temp_path = temp.name

    try:
        # Process PDF → extract narrative and metadata
        processed = fir_processor.process_fir_pdf(temp_path)

        # Analyze narrative with Gemini
        analysis = await gemini_service.analyze_narrative(processed["narrative"])

        # Create FIR record
        fir = FIR(
            file_name=file.filename,
            fir_number=processed.get("fir_number"),
            narrative=processed["narrative"],
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
        embedding = embedding_engine.encode_narrative(processed["narrative"])
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

        # Find similar FIRs
        similar = await _find_similar_in_db(processed["narrative"], db, exclude_id=fir.id)

        return AnalysisResult(
            crime_type=analysis.get("crime_type"),
            severity=analysis.get("severity"),
            summary_en=analysis.get("summary_en"),
            ipc_sections=analysis.get("ipc_sections"),
            recommended_steps=analysis.get("recommended_steps"),
            key_entities=analysis.get("key_entities"),
            similar_firs=similar
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
    """
    analysis = await gemini_service.analyze_narrative(request.narrative)
    similar = await _find_similar_in_db(request.narrative, db, top_k=request.top_k)

    return AnalysisResult(
        crime_type=analysis.get("crime_type"),
        severity=analysis.get("severity"),
        summary_en=analysis.get("summary_en"),
        ipc_sections=analysis.get("ipc_sections"),
        recommended_steps=analysis.get("recommended_steps"),
        key_entities=analysis.get("key_entities"),
        similar_firs=similar
    )


@router.post("/analyze-and-save", response_model=FIRDetail)
async def analyze_and_save_narrative(
    request: NarrativeAnalyzeRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Analyze a narrative and save it as a new FIR in the database.
    """
    analysis = await gemini_service.analyze_narrative(request.narrative)

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


@router.post("/bulk-upload", response_model=BulkUploadResponse)
async def bulk_upload_firs(
    files: List[UploadFile] = File(...),
    db: AsyncSession = Depends(get_db)
):
    """
    Bulk upload multiple FIR PDFs.
    Processes each one: extract narrative → analyze → store in DB.
    Designed for uploading previous/historical FIRs.
    """
    total = len(files)
    processed_count = 0
    errors = []

    for file in files:
        if not file.filename.endswith(".pdf"):
            errors.append(f"{file.filename}: Not a PDF file")
            continue

        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp:
                content = await file.read()
                temp.write(content)
                temp_path = temp.name

            # Process PDF
            processed = fir_processor.process_fir_pdf(temp_path)

            # Analyze narrative with Gemini
            try:
                analysis = await gemini_service.analyze_narrative(processed["narrative"])
            except Exception:
                analysis = gemini_service._fallback_analysis(processed["narrative"])

            # Create FIR record
            fir = FIR(
                file_name=file.filename,
                narrative=processed["narrative"],
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

            embedding = embedding_engine.encode_narrative(processed["narrative"])
            fir.embedding_vector = embedding.tobytes()

            db.add(fir)

            # Add accused
            for acc in processed.get("accused", []):
                db.add(Accused(fir_id=None, name=acc.get("name"),
                               father_name=acc.get("father_name")))

            await db.flush()
            processed_count += 1

            os.unlink(temp_path)

        except Exception as e:
            errors.append(f"{file.filename}: {str(e)}")

    await db.commit()

    return BulkUploadResponse(
        total_files=total,
        processed=processed_count,
        failed=total - processed_count,
        errors=errors
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
    """
    total = len(files)
    processed_count = 0
    errors = []

    for file in files:
        try:
            content = await file.read()
            data = json.loads(content.decode("utf-8"))

            narrative = data.get("narrative", "").strip()
            if not narrative:
                errors.append(f"{file.filename}: No narrative found")
                continue

            # Analyze narrative
            try:
                analysis = await gemini_service.analyze_narrative(narrative)
            except Exception:
                analysis = gemini_service._fallback_analysis(narrative)

            fir = FIR(
                file_name=data.get("file", file.filename),
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

            # Add accused from JSON
            for acc in data.get("accused", []):
                if acc.get("name"):
                    db.add(Accused(name=acc["name"],
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
        failed=total - processed_count,
        errors=errors
    )


@router.get("/{fir_id}/similar", response_model=List[SimilarFIR])
async def get_similar_firs(
    fir_id: int,
    top_k: int = Query(5, ge=1, le=20),
    db: AsyncSession = Depends(get_db)
):
    """Find FIRs similar to a specific FIR based on narrative similarity."""
    result = await db.execute(select(FIR).where(FIR.id == fir_id))
    fir = result.scalar_one_or_none()

    if not fir:
        raise HTTPException(status_code=404, detail="FIR not found")

    return await _find_similar_in_db(fir.narrative, db, top_k=top_k, exclude_id=fir.id)


# ──────────────────────── Helper Functions ────────────────────────

async def _find_similar_in_db(narrative: str, db: AsyncSession, top_k: int = 5, exclude_id: int = None, min_score: float = 0.55) -> List[SimilarFIR]:
    """Find similar FIRs in the database using embedding similarity.
    Only returns results with similarity score >= min_score to avoid false positives."""
    # Get all FIRs with embeddings
    query = select(FIR).where(FIR.embedding_vector.isnot(None))
    if exclude_id:
        query = query.where(FIR.id != exclude_id)

    result = await db.execute(query)
    all_firs = result.scalars().all()

    if not all_firs:
        return []

    # Encode the query narrative
    query_embedding = embedding_engine.encode_narrative(narrative).reshape(1, -1)

    # Compare with all stored embeddings
    similarities = []
    for fir in all_firs:
        if fir.embedding_vector:
            stored_emb = np.frombuffer(fir.embedding_vector, dtype=np.float32).reshape(1, -1)
            sim = float(np.dot(query_embedding, stored_emb.T)[0][0])
            # Only include results above the minimum similarity threshold
            if sim >= min_score:
                similarities.append((fir, sim))

    # Sort by similarity
    similarities.sort(key=lambda x: x[1], reverse=True)

    return [
        SimilarFIR(
            id=fir.id,
            file_name=fir.file_name,
            crime_type=fir.crime_type,
            severity=fir.severity,
            narrative=fir.narrative[:300] if fir.narrative else None,
            summary_en=fir.summary_en,
            similarity_score=round(score, 4),
            acts=fir.acts
        )
        for fir, score in similarities[:top_k]
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
    return None
