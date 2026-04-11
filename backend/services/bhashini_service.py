"""
Bhashini Translation Service
-----------------------------
Integrates with Bhashini API for Malayalam ↔ English translation.
Used for translating FIR narratives.
"""

import httpx
from typing import Optional
from config import get_settings

settings = get_settings()

BHASHINI_PIPELINE_URL = "https://dhruva-api.bhashini.gov.in/services/inference/pipeline"


async def translate_text(
    text: str,
    source_lang: str = "ml",
    target_lang: str = "en"
) -> Optional[str]:
    """
    Translate text using Bhashini API.

    Args:
        text: Input text to translate
        source_lang: Source language code (ml=Malayalam, en=English)
        target_lang: Target language code

    Returns:
        Translated text or None if translation fails
    """
    if not settings.BHASHINI_API_KEY:
        return _fallback_translate(text, source_lang, target_lang)

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
                        return output[0].get("target", text)

            print(f"[BhashiniService] API response status: {response.status_code}")
            return _fallback_translate(text, source_lang, target_lang)

    except Exception as e:
        print(f"[BhashiniService] Translation error: {e}")
        return _fallback_translate(text, source_lang, target_lang)


def _fallback_translate(text: str, source_lang: str, target_lang: str) -> str:
    """Fallback when Bhashini API is not available."""
    if source_lang == target_lang:
        return text

    return f"[Translation unavailable - Bhashini API not configured] Original ({source_lang}): {text[:500]}"
