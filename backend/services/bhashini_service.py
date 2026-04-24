"""
Translation Service
-------------------
Primary:  Bhashini API for Malayalam ↔ English translation.
Fallback: Google Translate (via googletrans) when Bhashini is
          not configured or returns an error.

Used for translating FIR narratives.
"""

import asyncio
import httpx
from typing import Optional, Tuple
from config import get_settings

settings = get_settings()

BHASHINI_PIPELINE_URL = "https://dhruva-api.bhashini.gov.in/services/inference/pipeline"

# Language code mapping: our internal codes → Google Translate codes
_LANG_MAP_GOOGLE = {"ml": "ml", "en": "en", "hi": "hi"}


async def translate_text(
    text: str,
    source_lang: str = "ml",
    target_lang: str = "en"
) -> Optional[str]:
    """
    Translate text, trying Bhashini first, then Google Translate as fallback.

    Returns:
        Translated text string, or the original text if all methods fail.
    """
    translated, engine = await translate_text_with_engine(text, source_lang, target_lang)
    return translated


async def translate_text_with_engine(
    text: str,
    source_lang: str = "ml",
    target_lang: str = "en"
) -> Tuple[str, str]:
    """
    Translate text and also report which engine was used.

    Returns:
        (translated_text, engine_name) where engine_name is
        'bhashini', 'google', or 'none'.
    """
    if source_lang == target_lang:
        return text, "none"

    # ── Try Bhashini first ──
    if settings.BHASHINI_API_KEY:
        result = await _bhashini_translate(text, source_lang, target_lang)
        if result is not None:
            return result, "bhashini"

    # ── Fallback: Google Translate ──
    result = await _google_translate(text, source_lang, target_lang)
    if result is not None:
        return result, "google"

    # ── All methods failed ──
    return text, "none"


# ─────────────────────── Bhashini ───────────────────────

async def _bhashini_translate(
    text: str, source_lang: str, target_lang: str
) -> Optional[str]:
    """Translate using Bhashini API. Returns None on failure."""
    try:
        headers = {
            "Content-Type": "application/json",
            "Authorization": settings.BHASHINI_API_KEY,
        }

        payload = {
            "pipelineTasks": [
                {
                    "taskType": "translation",
                    "config": {
                        "language": {
                            "sourceLanguage": source_lang,
                            "targetLanguage": target_lang
                        },
                        "serviceId": "ai4bharat/indictrans-v2-all-gpu--t4"
                    }
                }
            ],
            "inputData": {
                "input": [
                    {"source": text}
                ]
            }
        }

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                BHASHINI_PIPELINE_URL,
                json=payload,
                headers=headers
            )

            if response.status_code == 200:
                data = response.json()
                translations = data.get("pipelineResponse", [{}])
                if translations:
                    output = translations[0].get("output", [{}])
                    if output:
                        translated = output[0].get("target")
                        if translated:
                            return translated

            print(f"[BhashiniService] API response status: {response.status_code}")
            return None

    except Exception as e:
        print(f"[BhashiniService] Translation error: {e}")
        return None


# ─────────────────────── Google Translate Fallback ───────────────────────

async def _google_translate(
    text: str, source_lang: str, target_lang: str
) -> Optional[str]:
    """
    Translate using deep-translator library (free Google Translate API).
    Runs in a thread pool since deep-translator is synchronous.
    """
    try:
        from deep_translator import GoogleTranslator

        src = _LANG_MAP_GOOGLE.get(source_lang, source_lang)
        dest = _LANG_MAP_GOOGLE.get(target_lang, target_lang)

        # deep-translator uses 'auto' for auto-detection; we pass explicit codes
        translator = GoogleTranslator(source=src, target=dest)

        # Split long text into chunks (Google Translate has a ~5000 char limit)
        max_chunk = 4500
        if len(text) <= max_chunk:
            result = await asyncio.to_thread(translator.translate, text)
        else:
            # Translate in chunks and join
            chunks = [text[i:i + max_chunk] for i in range(0, len(text), max_chunk)]
            translated_chunks = []
            for chunk in chunks:
                translated = await asyncio.to_thread(translator.translate, chunk)
                translated_chunks.append(translated)
            result = " ".join(translated_chunks)

        if result:
            print(f"[TranslationService] Google Translate fallback used ({src}→{dest})")
            return result

        return None

    except ImportError:
        print("[TranslationService] deep-translator not installed — fallback unavailable")
        return None
    except Exception as e:
        print(f"[TranslationService] Google Translate error: {e}")
        return None
