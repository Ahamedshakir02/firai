"""
FirAI Engine — Main Inference Service
======================================
Drop-in replacement for gemini_service.py.
Uses 100% custom-built AI models. No external AI APIs.

Provides:
  - analyze_narrative()  → Crime type, severity, summary, entities, sections, steps
  - legal_query()        → Legal Q&A using knowledge base
  - detect_mo_patterns() → Modus operandi detection via clustering
"""

import asyncio
import re
from typing import Optional

from ai_engine.models.classifier import FirClassifier
from ai_engine.data.legal_corpus import get_investigation_steps, get_sections_by_crime, LEGAL_CORPUS
from ai_engine.data.label_generator import derive_labels


# ── Singleton instances ──
_classifier: Optional[FirClassifier] = None


def _get_classifier() -> FirClassifier:
    """Get or create the crime classifier (singleton)."""
    global _classifier
    if _classifier is None:
        _classifier = FirClassifier()
        _classifier.load()  # Will use fallback if model not yet trained
    return _classifier


def warmup():
    """Pre-load models at startup."""
    print("[FirAI Engine] Warming up custom AI models...")
    _get_classifier()
    print(f"[FirAI Engine] Ready. Legal corpus: {len(LEGAL_CORPUS)} sections loaded.")


# ══════════════════ ENTITY EXTRACTION ══════════════════

def _extract_entities(narrative: str) -> dict:
    """
    Rule-based + regex entity extraction from FIR narrative.
    Handles both Malayalam and English text.
    Will be replaced by custom NER model in Phase 2.
    """
    entities = {
        "victims": [],
        "accused": [],
        "locations": [],
        "weapons": [],
        "amounts": [],
        "vehicles": [],
        "time": "",
        "phone_numbers": [],
    }

    # Vehicle numbers (Kerala format: KL XX X XXXX)
    vehicles = re.findall(r'KL\s*\d{1,2}\s*[A-Z]?\s*\d{3,4}', narrative, re.IGNORECASE)
    entities["vehicles"] = list(set(vehicles))

    # Monetary amounts
    amounts = re.findall(r'(\d[\d,]*/?-?\s*രൂപ[ായ]*|\d[\d,]*/-)', narrative)
    if not amounts:
        amounts = re.findall(r'Rs\.?\s*(\d[\d,]*)', narrative, re.IGNORECASE)
    entities["amounts"] = [a.strip() for a in amounts] if amounts else []

    # Phone numbers
    phones = re.findall(r'\b(\d{10})\b', narrative)
    entities["phone_numbers"] = phones

    # Time extraction (Malayalam format: XX.XX മണിക്ക്)
    times = re.findall(r'(\d{1,2}[.:]\d{2}\s*മണി[ക്]*)', narrative)
    if not times:
        times = re.findall(r'(\d{1,2}:\d{2}\s*(?:hrs|am|pm))', narrative, re.IGNORECASE)
    entities["time"] = times[0] if times else ""

    # Date extraction
    dates = re.findall(r'(\d{1,2}[./]\d{1,2}[./]\d{2,4})', narrative)
    if dates and not entities["time"]:
        entities["time"] = dates[0]

    # Weapon keywords (Malayalam + English)
    weapon_keywords = {
        "ജാക്കി ലിവര്‍": "jack lever", "കത്തി": "knife",
        "ലാത്തി": "lathi", "വടി": "stick", "കല്ല്": "stone",
        "ഇരുമ്പ്": "iron rod", "knife": "knife", "rod": "rod",
        "sword": "sword", "axe": "axe", "gun": "gun",
    }
    for ml, en in weapon_keywords.items():
        if ml in narrative or en in narrative.lower():
            entities["weapons"].append(en)

    # Location indicators (Malayalam)
    loc_patterns = [
        r'(\w+\s+എന്ന\s+സ്ഥലത്ത്)',  # "X enна sthalaтт"
        r'(\w+\s+റോഡില്‍)',  # "X roadil"
        r'(\w+\s+ജംഗ്ഷന)',  # "X junction"
        r'(\w+\s+ബസ്[സ്]*\s*സ്റ്റാന്[റഡ]*)',  # bus stand
    ]
    for pat in loc_patterns:
        matches = re.findall(pat, narrative)
        entities["locations"].extend(matches[:3])

    return entities


# ══════════════════ SUMMARIZER ══════════════════

def _generate_summary(narrative: str, crime_type: str, entities: dict) -> str:
    """
    Generate an English summary using extractive + template approach.
    Will be enhanced with TextRank in Phase 2.
    """
    # Try to extract key facts for template
    time_str = entities.get("time", "an unknown time")
    locations = entities.get("locations", [])
    location_str = locations[0] if locations else "an unspecified location"
    amounts = entities.get("amounts", [])
    vehicles = entities.get("vehicles", [])
    weapons = entities.get("weapons", [])

    # Crime type descriptions
    crime_desc = {
        "assault": "an assault incident",
        "theft": "a theft",
        "robbery": "a robbery",
        "murder": "a murder",
        "drunk_driving": "a drunk driving offense",
        "rash_driving": "a rash/negligent driving offense",
        "cheating": "a cheating/fraud case",
        "forgery": "a forgery case",
        "sexual_offense": "a sexual offense",
        "criminal_intimidation": "a criminal intimidation incident",
        "excise_offense": "an excise/liquor offense",
        "unnatural_death": "an unnatural death case",
        "trespass": "a criminal trespass",
        "property_damage": "a property damage incident",
        "domestic_violence": "a domestic violence case",
        "kidnapping": "a kidnapping case",
        "cyber_crime": "a cyber crime",
        "drug_offense": "a drug offense",
    }.get(crime_type, f"a {crime_type.replace('_', ' ')} case")

    # Build summary
    parts = [f"FIR reports {crime_desc}"]

    if time_str:
        parts.append(f"occurring at {time_str}")
    if location_str and location_str != "an unspecified location":
        parts.append(f"near {location_str}")

    summary = " ".join(parts) + "."

    if vehicles:
        summary += f" Vehicle(s) involved: {', '.join(vehicles)}."
    if amounts:
        summary += f" Financial loss: {', '.join(amounts)}."
    if weapons:
        summary += f" Weapon(s) used: {', '.join(weapons)}."

    # Truncate narrative and add it
    narr_preview = narrative[:200].replace('\n', ' ')
    summary += f" Narrative excerpt: {narr_preview}..."

    return summary


# ══════════════════ IPC/BNS SECTION MAPPING ══════════════════

def _map_legal_sections(crime_type: str) -> list:
    """Map crime type to relevant IPC/BNS sections using the legal corpus."""
    sections = get_sections_by_crime(crime_type)
    result = []
    for s in sections:
        result.append({
            "section": s["section"],
            "act": s["act"],
            "description": s["title"],
        })
    return result if result else [{"section": "N/A", "act": "N/A", "description": "Section mapping pending — model training in progress"}]


# ══════════════════ MAIN API: analyze_narrative ══════════════════

async def analyze_narrative(narrative: str) -> dict:
    """
    Analyze an FIR narrative using custom AI models.
    Drop-in replacement for gemini_service.analyze_narrative().

    Returns:
        {crime_type, severity, summary_en, ipc_sections,
         recommended_steps, key_entities}
    """
    classifier = _get_classifier()

    # Run classification in thread pool (non-blocking)
    prediction = await asyncio.to_thread(classifier.predict, narrative)

    crime_type = prediction["crime_type"]
    severity = prediction["severity"]

    # Extract entities
    entities = _extract_entities(narrative)

    # Generate summary
    summary = _generate_summary(narrative, crime_type, entities)

    # Map legal sections
    ipc_sections = _map_legal_sections(crime_type)

    # Get investigation steps from legal corpus
    steps = get_investigation_steps(crime_type)

    return {
        "crime_type": crime_type,
        "severity": severity,
        "summary_en": summary,
        "ipc_sections": ipc_sections,
        "recommended_steps": steps,
        "key_entities": entities,
        "ai_confidence": prediction.get("crime_confidence", 0),
        "model": "firai-engine-v1",
    }


# ══════════════════ LEGAL Q&A ══════════════════

async def legal_query(question: str, context_narrative: str = "") -> dict:
    """
    Answer legal questions using the built-in legal corpus.
    Phase 2 will add a custom transformer for more nuanced answers.
    """
    question_lower = question.lower()

    # Search legal corpus for relevant sections
    relevant = []
    for section in LEGAL_CORPUS:
        score = 0
        # Check title match
        if any(word in section["title"].lower() for word in question_lower.split()):
            score += 2
        # Check description match
        if any(word in section["description"].lower() for word in question_lower.split() if len(word) > 3):
            score += 1
        # Check crime type match
        if section["crime_type"] in question_lower:
            score += 3
        if score > 0:
            relevant.append((score, section))

    relevant.sort(key=lambda x: x[0], reverse=True)
    top_sections = [s for _, s in relevant[:5]]

    if not top_sections:
        return {
            "answer": "No relevant legal sections found for your query. Please try rephrasing with specific legal terms or crime types.",
            "relevant_sections": [],
        }

    # Build answer from corpus
    answer_parts = []
    sections_list = []
    for s in top_sections:
        answer_parts.append(f"**{s['act']} Section {s['section']} — {s['title']}**: {s['description']}")
        answer_parts.append(f"Punishment: {s['punishment']}")
        if s.get("elements"):
            answer_parts.append(f"Elements: {', '.join(s['elements'])}")
        answer_parts.append("")
        sections_list.append({
            "section": s["section"],
            "act": s["act"],
            "description": s["title"],
        })

    return {
        "answer": "\n".join(answer_parts),
        "relevant_sections": sections_list,
    }


# ══════════════════ MO PATTERN DETECTION ══════════════════

async def detect_mo_patterns(narratives: list) -> list:
    """
    Detect MO patterns using classifier predictions + clustering.
    No Gemini needed — uses our custom crime classifier.
    """
    if not narratives or len(narratives) < 2:
        return []

    classifier = _get_classifier()
    classified = []
    for narr in narratives:
        pred = classifier.predict(narr)
        classified.append(pred)

    # Group by crime type
    from collections import defaultdict
    groups = defaultdict(list)
    for i, pred in enumerate(classified):
        groups[pred["crime_type"]].append(i)

    patterns = []
    for crime_type, indices in groups.items():
        if len(indices) >= 2:
            patterns.append({
                "pattern_name": f"{crime_type.replace('_', ' ').title()} Pattern",
                "description": f"Group of {len(indices)} FIRs classified as {crime_type}",
                "crime_type": crime_type,
                "linked_firs": indices,
                "occurrence_count": len(indices),
            })

    return patterns


# ══════════════════ FALLBACK (compatibility) ══════════════════

def _fallback_analysis(narrative: str) -> dict:
    """Synchronous fallback for compatibility with existing code."""
    classifier = _get_classifier()
    prediction = classifier.predict(narrative)
    entities = _extract_entities(narrative)
    summary = _generate_summary(narrative, prediction["crime_type"], entities)
    steps = get_investigation_steps(prediction["crime_type"])

    return {
        "crime_type": prediction["crime_type"],
        "severity": prediction["severity"],
        "summary_en": summary,
        "ipc_sections": _map_legal_sections(prediction["crime_type"]),
        "recommended_steps": steps,
        "key_entities": entities,
        "model": "firai-engine-v1-fallback",
    }
