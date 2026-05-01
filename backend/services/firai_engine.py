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
    Supports:
      - Direct section lookup: "IPC 302", "BNS 103", "section 324"
      - Bail queries: "Is 420 bailable?", "bail for IPC 324"
      - Crime type queries: "theft", "kidnapping", "cyber crime"
      - Investigation queries: "steps for murder investigation"
      - General keyword search as fallback
    """
    question_lower = question.lower()

    # ── Fast-path: direct section number lookup ──
    section_match = _extract_section_from_query(question)
    if section_match:
        act_hint, section_num = section_match
        direct_results = _find_section_in_corpus(act_hint, section_num)
        if direct_results:
            return _format_section_response(direct_results, question_lower)

    # ── Crime type matching ──
    crime_type_match = _detect_crime_type(question_lower)
    if crime_type_match:
        sections = get_sections_by_crime(crime_type_match)
        if sections:
            return _format_crime_type_response(sections, crime_type_match, question_lower)

    # ── Keyword search fallback (improved scoring) ──
    relevant = []
    # Filter out very short/common words
    query_words = [w for w in question_lower.split() if len(w) > 2 and w not in {
        "what", "the", "for", "and", "how", "who", "can", "are", "was", "has",
        "does", "this", "that", "with", "from", "about", "which", "where",
        "section", "act", "under", "punishment", "bailable", "bail",
    }]

    for section in LEGAL_CORPUS:
        score = 0
        title_lower = section["title"].lower()
        desc_lower = section["description"].lower()

        # Title word match (high weight)
        for word in query_words:
            if word in title_lower:
                score += 3
            if word in desc_lower:
                score += 1
        # Crime type match
        if section["crime_type"].replace("_", " ") in question_lower:
            score += 4
        # Elements match
        for element in section.get("elements", []):
            if any(w in element.lower() for w in query_words):
                score += 2
                break

        if score > 0:
            relevant.append((score, section))

    relevant.sort(key=lambda x: x[0], reverse=True)
    top_sections = [s for _, s in relevant[:5]]

    if not top_sections:
        return {
            "answer": "No relevant legal sections found for your query. Try asking with:\n"
                      "• A specific section number (e.g., \"IPC 302\", \"BNS 115\")\n"
                      "• A crime type (e.g., \"theft\", \"kidnapping\", \"cyber crime\")\n"
                      "• A legal question (e.g., \"Is 420 bailable?\", \"punishment for robbery\")",
            "relevant_sections": [],
        }

    return _format_section_response(top_sections, question_lower)


def _extract_section_from_query(question: str) -> tuple:
    """
    Extract (act_hint, section_number) from a query.
    Handles: "IPC 302", "BNS 115(2)", "section 324", "420", "NDPS 20"
    """
    q = question.strip()

    # Pattern: "IPC 302", "BNS 115(2)", "NDPS Act 20", "IT Act 66C"
    import re
    act_section = re.search(
        r'\b(IPC|BNS|BNSS|NDPS|POCSO|IT\s*Act|Arms\s*Act|Abkari|MV\s*Act|Motor\s*Vehicle|SC/ST|CrPC)'
        r'\s*(?:Act\s*)?(?:Section\s*)?(\d+[A-Za-z]?(?:\([^)]*\))?)',
        q, re.IGNORECASE
    )
    if act_section:
        return act_section.group(1).strip(), act_section.group(2).strip()

    # Pattern: "section 302", "sec 420", "§302"
    sec_match = re.search(r'(?:section|sec\.?|§)\s*(\d+[A-Za-z]?(?:\([^)]*\))?)', q, re.IGNORECASE)
    if sec_match:
        return None, sec_match.group(1).strip()

    # Pattern: bare number like "302" or "420" if query is short
    if len(q.split()) <= 4:
        bare_num = re.search(r'\b(\d{2,3}[A-Za-z]?(?:\([^)]*\))?)\b', q)
        if bare_num:
            num = bare_num.group(1)
            # Avoid matching years like 2025
            if not re.match(r'^(19|20)\d{2}$', num):
                return None, num

    return None


def _find_section_in_corpus(act_hint: str, section_num: str) -> list:
    """Find matching sections in LEGAL_CORPUS."""
    results = []

    for entry in LEGAL_CORPUS:
        if entry["section"] != section_num:
            continue

        if act_hint:
            act_upper = act_hint.upper().replace(" ", "")
            entry_act_upper = entry["act"].upper().replace(" ", "")
            # Check if act hint matches
            if act_upper not in entry_act_upper and entry_act_upper not in act_upper:
                # Also check common abbreviations
                if not (act_upper in ("IT", "ITACT") and "IT" in entry_act_upper):
                    continue

        results.append(entry)

    # If no act hint, return all matches for that section number
    if not results and not act_hint:
        for entry in LEGAL_CORPUS:
            if entry["section"] == section_num:
                results.append(entry)

    return results


def _detect_crime_type(question_lower: str) -> str:
    """Detect if the question is about a specific crime type."""
    CRIME_KEYWORDS = {
        "murder": ["murder", "killing", "homicide"],
        "assault": ["assault", "hurt", "beating", "attack", "grievous"],
        "theft": ["theft", "stealing", "stolen", "pickpocket"],
        "robbery": ["robbery", "robbing", "snatch", "snatching"],
        "cheating": ["cheating", "fraud", "scam", "swindle"],
        "kidnapping": ["kidnapping", "abduction", "kidnap", "abduct", "missing child"],
        "sexual_offense": ["sexual", "rape", "molestation", "modesty", "pocso"],
        "domestic_violence": ["domestic violence", "dowry", "cruelty by husband", "498a"],
        "cyber_crime": ["cyber", "hacking", "online fraud", "identity theft", "phishing"],
        "drug_offense": ["drug", "ndps", "ganja", "heroin", "narcotics", "cannabis"],
        "drunk_driving": ["drunk driving", "drunken driving", "alcohol driving"],
        "rash_driving": ["rash driving", "negligent driving", "road accident", "hit and run"],
        "extortion": ["extortion", "hafta", "threatening for money"],
        "dacoity": ["dacoity", "gang robbery"],
        "forgery": ["forgery", "fake document", "forged"],
        "trespass": ["trespass", "illegal entry"],
        "criminal_intimidation": ["intimidation", "threatening", "death threat"],
        "excise_offense": ["excise", "abkari", "liquor", "illicit alcohol"],
        "property_damage": ["property damage", "mischief", "vandalism"],
        "unnatural_death": ["unnatural death", "suspicious death", "drowning"],
        "death_by_negligence": ["death by negligence", "negligent death", "304a"],
        "atrocity": ["sc/st", "caste", "atrocity", "dalit"],
        "arms_offense": ["illegal arms", "unlicensed gun", "firearm", "arms act"],
        "missing_person": ["missing person", "missing child", "person missing"],
        "breach_of_trust": ["breach of trust", "misappropriation", "embezzlement"],
    }

    for crime_type, keywords in CRIME_KEYWORDS.items():
        if any(kw in question_lower for kw in keywords):
            return crime_type
    return None


def _format_section_response(sections: list, question_lower: str) -> dict:
    """Format a response from matched sections."""
    is_bail_query = any(w in question_lower for w in ["bail", "bailable"])
    is_steps_query = any(w in question_lower for w in ["investigation", "steps", "procedure", "how to investigate"])

    answer_parts = []
    sections_list = []

    for s in sections:
        # Section header
        answer_parts.append(f"**{s['act']} Section {s['section']} — {s['title']}**")
        answer_parts.append(f"{s['description']}")
        answer_parts.append(f"")
        answer_parts.append(f"**Punishment:** {s['punishment']}")

        # Bail info (always include, highlight if bail query)
        bail_status = "Yes ✅" if s.get("bailable") else ("No ❌" if s.get("bailable") is False else "N/A")
        cognizable = "Yes" if s.get("cognizable") else ("No" if s.get("cognizable") is False else "N/A")
        answer_parts.append(f"**Bailable:** {bail_status}  |  **Cognizable:** {cognizable}")

        if s.get("elements"):
            answer_parts.append(f"**Elements of offence:** {', '.join(s['elements'])}")

        # Investigation steps (always include if available)
        if s.get("investigation_steps"):
            if is_steps_query:
                answer_parts.append(f"\n**Investigation Steps:**")
                for i, step in enumerate(s["investigation_steps"], 1):
                    answer_parts.append(f"  {i}. {step}")
            else:
                answer_parts.append(f"**Key investigation steps:** {'; '.join(s['investigation_steps'][:4])}")

        answer_parts.append("")
        answer_parts.append("---")
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


def _format_crime_type_response(sections: list, crime_type: str, question_lower: str) -> dict:
    """Format a response for a crime type query."""
    crime_label = crime_type.replace("_", " ").title()
    answer_parts = [f"**Legal sections related to {crime_label}:**\n"]

    sections_list = []
    for s in sections:
        answer_parts.append(f"**{s['act']} Section {s['section']} — {s['title']}**")
        answer_parts.append(f"Punishment: {s['punishment']}")
        bail = "Yes ✅" if s.get("bailable") else ("No ❌" if s.get("bailable") is False else "N/A")
        answer_parts.append(f"Bailable: {bail}")
        answer_parts.append("")

        sections_list.append({
            "section": s["section"],
            "act": s["act"],
            "description": s["title"],
        })

    # Add investigation steps for this crime type
    steps = get_investigation_steps(crime_type)
    if steps:
        answer_parts.append("**Recommended Investigation Steps:**")
        for i, step in enumerate(steps[:8], 1):
            answer_parts.append(f"  {i}. {step}")

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
