"""
Translation Router
------------------
Endpoints for Malayalam ↔ English translation.
Uses Bhashini API (primary) with Google Translate fallback.
"""

from fastapi import APIRouter, Depends
from schemas.fir import TranslateRequest, TranslateResponse
from services import bhashini_service
from models.officer import Officer
from routers.auth import require_officer

router = APIRouter(prefix="/api/translate", tags=["Translation"])


@router.post("", response_model=TranslateResponse)
async def translate_text(request: TranslateRequest, officer: Officer = Depends(require_officer)):
    """
    Translate text between Malayalam and English.
    Tries Bhashini API first; falls back to Google Translate automatically.
    """
    translated, engine = await bhashini_service.translate_text_with_engine(
        text=request.text,
        source_lang=request.source_lang,
        target_lang=request.target_lang
    )

    return TranslateResponse(
        original_text=request.text,
        translated_text=translated,
        source_lang=request.source_lang,
        target_lang=request.target_lang,
        engine=engine
    )
