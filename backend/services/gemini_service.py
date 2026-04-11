"""
Gemini LLM Service
------------------
Integrates with Google Gemini API to analyze FIR narratives.
Handles: crime classification, risk scoring, legal section mapping,
investigation recommendations, and English summarization.

Supports narratives in both Malayalam and English.
"""

import json
import re
from typing import Optional
import google.generativeai as genai
from config import get_settings

settings = get_settings()

# Configure Gemini
if settings.GEMINI_API_KEY:
    genai.configure(api_key=settings.GEMINI_API_KEY)


def _get_model():
    """Get a Gemini model instance."""
    return genai.GenerativeModel("gemini-1.5-flash")


async def analyze_narrative(narrative: str) -> dict:
    """
    Analyze an FIR narrative using Gemini.
    The narrative can be in Malayalam or English.

    Returns structured analysis:
    - crime_type, severity, risk_score
    - summary_en (English summary)
    - ipc_sections
    - recommended_steps
    - key_entities
    """
    if not settings.GEMINI_API_KEY:
        return _fallback_analysis(narrative)

    try:
        model = _get_model()

        prompt = f"""You are an expert Kerala Police investigation AI assistant.
Analyze the following FIR narrative text. The narrative may be in Malayalam or English.

FIR NARRATIVE:
\"\"\"{narrative}\"\"\"

Analyze this narrative and return a JSON object with the following fields:
{{
    "crime_type": "one of: assault, theft, robbery, cheating, trespass, murder, kidnapping, sexual_offense, cyber_crime, drug_offense, traffic_accident, domestic_violence, property_damage, fraud, other",
    "severity": "one of: low, medium, high, critical",
    "risk_score": "a number from 1 to 10 (10 = highest risk)",
    "summary_en": "A clear English summary of the incident described in the narrative (2-3 sentences)",
    "ipc_sections": [
        {{"section": "section number", "act": "IPC or BNS", "description": "brief description of the section"}}
    ],
    "recommended_steps": [
        "step 1 for investigation",
        "step 2 for investigation"
    ],
    "key_entities": {{
        "victims": ["name or description"],
        "accused": ["name or description"],
        "locations": ["location names"],
        "weapons": ["weapon if any"],
        "amounts": ["monetary amounts if any"],
        "time": "when did it happen"
    }}
}}

Return ONLY valid JSON. No markdown, no code blocks, no explanation.
"""

        response = model.generate_content(prompt)
        text = response.text.strip()

        # Clean up response - remove markdown code blocks if present
        text = re.sub(r'^```json\s*', '', text)
        text = re.sub(r'^```\s*', '', text)
        text = re.sub(r'\s*```$', '', text)

        result = json.loads(text)
        return result

    except Exception as e:
        print(f"[GeminiService] Error analyzing narrative: {e}")
        return _fallback_analysis(narrative)


async def legal_query(question: str, context_narrative: str = "") -> dict:
    """
    Answer a legal question using Gemini, optionally with FIR narrative context.
    """
    if not settings.GEMINI_API_KEY:
        return {
            "answer": "Gemini API key not configured. Please set GEMINI_API_KEY in your .env file.",
            "relevant_sections": [],
            "source_firs": []
        }

    try:
        model = _get_model()

        context_part = ""
        if context_narrative:
            context_part = f"""

RELATED FIR NARRATIVE (for context):
\"\"\"{context_narrative}\"\"\"
"""

        prompt = f"""You are an expert legal advisor for Kerala Police officers.
You have deep knowledge of Indian Penal Code (IPC), Bharatiya Nyaya Sanhita (BNS),
Code of Criminal Procedure (CrPC), Bharatiya Nagarik Suraksha Sanhita (BNSS),
and Kerala Police Act.
{context_part}

OFFICER'S QUESTION:
{question}

Provide a clear, practical answer that a police officer can immediately use.
Include:
1. Direct answer to the question
2. Relevant legal sections (IPC/BNS/CrPC/BNSS)
3. Procedural guidance if applicable
4. Any important caveats or exceptions

Return as JSON:
{{
    "answer": "detailed answer text",
    "relevant_sections": [
        {{"section": "number", "act": "act name", "description": "brief description"}}
    ]
}}

Return ONLY valid JSON.
"""

        response = model.generate_content(prompt)
        text = response.text.strip()
        text = re.sub(r'^```json\s*', '', text)
        text = re.sub(r'^```\s*', '', text)
        text = re.sub(r'\s*```$', '', text)

        return json.loads(text)

    except Exception as e:
        print(f"[GeminiService] Legal query error: {e}")
        return {
            "answer": f"Error processing query: {str(e)}",
            "relevant_sections": []
        }


async def detect_mo_patterns(narratives: list) -> list:
    """
    Analyze multiple FIR narratives to detect common modus operandi patterns.
    """
    if not settings.GEMINI_API_KEY or not narratives:
        return []

    try:
        model = _get_model()

        # Limit to 20 narratives to avoid token limits
        sample = narratives[:20]
        narratives_text = "\n---\n".join([f"FIR {i+1}: {n}" for i, n in enumerate(sample)])

        prompt = f"""You are a crime pattern analyst for Kerala Police.
Analyze the following FIR narratives and identify common Modus Operandi (MO) patterns.

NARRATIVES:
{narratives_text}

Identify recurring crime patterns, methods, and MO across these FIRs.
Return as JSON array:
[
    {{
        "pattern_name": "short name for the pattern",
        "description": "description of the MO pattern",
        "crime_type": "crime type",
        "linked_firs": [1, 2, 5],
        "occurrence_count": 3
    }}
]

Return ONLY valid JSON array.
"""

        response = model.generate_content(prompt)
        text = response.text.strip()
        text = re.sub(r'^```json\s*', '', text)
        text = re.sub(r'^```\s*', '', text)
        text = re.sub(r'\s*```$', '', text)

        return json.loads(text)

    except Exception as e:
        print(f"[GeminiService] MO detection error: {e}")
        return []


def _fallback_analysis(narrative: str) -> dict:
    """Fallback analysis when Gemini is not available."""
    # Simple keyword-based crime classification
    text_lower = narrative.lower()

    crime_type = "other"
    severity = "medium"
    risk_score = 5.0

    # Malayalam and English keyword matching
    if any(w in text_lower for w in ["murder", "kill", "കൊല", "death", "മരണം"]):
        crime_type = "murder"
        severity = "critical"
        risk_score = 10.0
    elif any(w in text_lower for w in ["theft", "steal", "stolen", "മോഷ്ടി", "robbery", "rob"]):
        crime_type = "theft"
        severity = "medium"
        risk_score = 6.0
    elif any(w in text_lower for w in ["assault", "attack", "beat", "hit", "അടിച്ച", "അടിക്ക", "ചവിട്ട"]):
        crime_type = "assault"
        severity = "high"
        risk_score = 7.0
    elif any(w in text_lower for w in ["cheat", "fraud", "ചതി", "വഞ്ചന"]):
        crime_type = "cheating"
        severity = "medium"
        risk_score = 5.0
    elif any(w in text_lower for w in ["trespass", "അതിക്രമിച്ച", "break in"]):
        crime_type = "trespass"
        severity = "high"
        risk_score = 7.0

    return {
        "crime_type": crime_type,
        "severity": severity,
        "risk_score": risk_score,
        "summary_en": f"FIR narrative classified as {crime_type} (fallback analysis - Gemini not available)",
        "ipc_sections": [],
        "recommended_steps": [
            "Record detailed witness statements",
            "Collect physical evidence from the crime scene",
            "Verify accused identity and location"
        ],
        "key_entities": {}
    }
