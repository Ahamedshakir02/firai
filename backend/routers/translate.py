"""
Translation Router
------------------
Endpoints for Malayalam ↔ English translation using Bhashini API.
Used for translating FIR narratives.
"""

from fastapi import APIRouter
from schemas.fir import TranslateRequest, TranslateResponse
from services import bhashini_service

router = APIRouter(prefix="/api/translate", tags=["Translation"])


@router.post("", response_model=TranslateResponse)
async def translate_text(request: TranslateRequest):
    """
    Translate text between Malayalam and English.
    Supports FIR narrative translation in both directions.
    """
    translated = await bhashini_service.translate_text(
        text=request.text,
        source_lang=request.source_lang,
        target_lang=request.target_lang
    )

    return TranslateResponse(
        original_text=request.text,
        translated_text=translated or request.text,
        source_lang=request.source_lang,
        target_lang=request.target_lang
    )
