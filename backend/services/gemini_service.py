"""
Gemini LLM Service
------------------
Integrates with Google Gemini API to analyze FIR narratives.
Handles: crime classification, legal section mapping,
investigation recommendations, and English summarization.

Supports narratives in both Malayalam and English.
"""

import json
import re
import asyncio
from typing import Optional
import google.generativeai as genai
from config import get_settings

settings = get_settings()

# Configure Gemini
if settings.GEMINI_API_KEY:
    genai.configure(api_key=settings.GEMINI_API_KEY)

# Reuse a single model instance (thread-safe for reads)
_model = None

def _get_model():
    """Get or create a Gemini model instance (module-level singleton)."""
    global _model
    if _model is None:
        _model = genai.GenerativeModel("gemini-1.5-flash")
    return _model


# Maximum narrative length to send to Gemini (prevents token limit errors)
MAX_NARRATIVE_LENGTH = 15_000


async def analyze_narrative(narrative: str) -> dict:
    """
    Analyze an FIR narrative using Gemini.
    The narrative can be in Malayalam or English.

    Returns structured analysis:
    - crime_type, severity
    - summary_en (English summary)
    - ipc_sections
    - recommended_steps
    - key_entities
    """
    if not settings.GEMINI_API_KEY:
        return _fallback_analysis(narrative)

    # Truncate very long narratives to avoid hitting Gemini token limits
    if len(narrative) > MAX_NARRATIVE_LENGTH:
        narrative = narrative[:MAX_NARRATIVE_LENGTH] + "\n[...truncated for analysis]"

    try:
        model = _get_model()

        prompt = f"""You are an expert Kerala Police investigation AI assistant.
Analyze the following FIR narrative text. The narrative may be in Malayalam or English.

FIR NARRATIVE:
\"\"\"{narrative}\"\"\"

Analyze this narrative and return a JSON object with the following fields:
{{
    "crime_type": "one of: assault, theft, robbery, cheating, trespass, murder, kidnapping, sexual_offense, cyber_crime, drug_offense, drunk_driving, road_accident, forgery, excise_offense, criminal_intimidation, unnatural_death, illegal_mining, missing_person, domestic_violence, property_damage, fraud, other",
    "severity": "one of: low, medium, high, critical",
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

        # Run the blocking Gemini SDK call in a thread pool — never block the event loop
        response = await asyncio.wait_for(
            asyncio.to_thread(model.generate_content, prompt),
            timeout=30.0
        )
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

        # Run blocking Gemini call in thread pool to avoid blocking the event loop
        response = await asyncio.wait_for(
            asyncio.to_thread(model.generate_content, prompt),
            timeout=30.0
        )
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

IMPORTANT INSTRUCTIONS:
- Focus ONLY on the actual CRIME METHOD, LOCATION PATTERNS, SUSPECT BEHAVIOR, and VICTIM TARGETING.
- Do NOT consider FIR format/template similarities as patterns (e.g., "complainant came to station", "statement recorded", "case registered" — these appear in every FIR and are NOT crime patterns).
- A valid MO pattern is when multiple crimes share similar methods (e.g., "drunk driving on NH road at night", "house break-in while owners are abroad", "online job fraud collecting money in installments").
- Only report patterns that appear in 2 or more FIRs.
- If no genuine crime patterns exist, return an empty array [].

NARRATIVES:
{narratives_text}

Identify recurring crime patterns, methods, and MO across these FIRs.
Return as JSON array:
[
    {{
        "pattern_name": "short descriptive name for the crime pattern",
        "description": "detailed description of the MO pattern — what method, where, when, how",
        "crime_type": "crime type category",
        "linked_firs": [1, 2, 5],
        "occurrence_count": 3
    }}
]

Return ONLY valid JSON array.
"""

        # Run blocking Gemini call in thread pool to avoid blocking the event loop
        response = await asyncio.wait_for(
            asyncio.to_thread(model.generate_content, prompt),
            timeout=60.0
        )
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

    # Malayalam and English keyword matching
    if any(w in text_lower for w in ["murder", "kill", "കൊല", "death", "മരണം", "കൊല്ലും"]):
        crime_type = "murder"
        severity = "critical"
    elif any(w in text_lower for w in ["മദ്യപിച്ച", "drunk driv", "ആല്‍ക്കോ", "breath analy", "alcohol", "മദ്യത്തിന്റെ", "281 of bns", "185 of mv", "485"]):
        crime_type = "drunk_driving"
        severity = "high"
    elif any(w in text_lower for w in ["road accident", "rash driv", "അശ്രദ്ധമായും", "അവിവേകമായും", "ബ്രേക്ക്", "motor vehicle", "negligent driving", "അതിവേഗതയിലും"]):
        crime_type = "road_accident"
        severity = "high"
    elif any(w in text_lower for w in ["theft", "steal", "stolen", "മോഷ്ടി", "robbery", "rob", "കളവ്", "കള്ളന്‍മാ"]):
        crime_type = "theft"
        severity = "medium"
    elif any(w in text_lower for w in ["assault", "attack", "beat", "hit", "അടിച്ച", "അടിക്ക", "ചവിട്ട", "ദേഹോപദ്രവം", "grievous hurt", "ഗുരുതര", "voluntarily causing hurt"]):
        crime_type = "assault"
        severity = "high"
    elif any(w in text_lower for w in ["cheat", "fraud", "ചതി", "വഞ്ചന", "വിശ്വാസ", "420", "318"]):
        crime_type = "cheating"
        severity = "medium"
    elif any(w in text_lower for w in ["trespass", "അതിക്രമിച്ച", "break in", "house breaking"]):
        crime_type = "trespass"
        severity = "high"
    elif any(w in text_lower for w in ["forg", "counterfeit", "വ്യാജരേഖ", "465", "468", "falsif"]):
        crime_type = "forgery"
        severity = "medium"
    elif any(w in text_lower for w in ["abkari", "excise", "മദ്യം", "liquor", "പരസ്യമായി മദ്യപിക്ക", "15(c)"]):
        crime_type = "excise_offense"
        severity = "medium"
    elif any(w in text_lower for w in ["threaten", "intimidat", "ഭീഷണിപ്പെടുത്തി", "506", "കൊല്ലുമെന്ന്"]):
        crime_type = "criminal_intimidation"
        severity = "high"
    elif any(w in text_lower for w in ["drown", "മുങ്ങി", "unnatural death", "മരണപ്പെട്ട്", "194", "suicide"]):
        crime_type = "unnatural_death"
        severity = "critical"
    elif any(w in text_lower for w in ["sand", "മണല്‍", "mining", "പുഴമണല്‍", "river bank", "305(e)"]):
        crime_type = "illegal_mining"
        severity = "medium"
    elif any(w in text_lower for w in ["missing", "കാണാതായ", "disappear"]):
        crime_type = "missing_person"
        severity = "high"

    return {
        "crime_type": crime_type,
        "severity": severity,
        "summary_en": f"FIR narrative classified as {crime_type} (fallback analysis - Gemini not available)",
        "ipc_sections": [],
        "recommended_steps": [
            "Record detailed witness statements",
            "Collect physical evidence from the crime scene",
            "Verify accused identity and location"
        ],
        "key_entities": {}
    }
