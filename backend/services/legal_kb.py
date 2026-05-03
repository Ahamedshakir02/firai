"""
Legal Knowledge Base Service
-----------------------------
Unified legal reference — derives ALL data from legal_corpus.py.
Single source of truth for both AI engine and Legal Reference panel.

Provides section descriptions, bail status, punishment details.
"""

from ai_engine.data.legal_corpus import LEGAL_CORPUS


def _build_section_index():
    """Build a fast lookup index: (act_key, section) → corpus entry."""
    index = {}
    for entry in LEGAL_CORPUS:
        act_upper = entry["act"].upper()
        section = entry["section"]

        # Normalize act names to standard keys
        if "IPC" in act_upper or "INDIAN PENAL" in act_upper:
            key = "IPC"
        elif "BNS" in act_upper and "BNSS" not in act_upper:
            key = "BNS"
        elif "BNSS" in act_upper:
            key = "BNSS"
        elif "ABKARI" in act_upper:
            key = "ABKARI"
        elif "MV" in act_upper or "MOTOR VEHICLE" in act_upper:
            key = "MV_ACT"
        elif "NDPS" in act_upper:
            key = "NDPS"
        elif "POCSO" in act_upper:
            key = "POCSO"
        elif "SC/ST" in act_upper or "POA" in act_upper:
            key = "SC_ST"
        elif "ARMS" in act_upper:
            key = "ARMS"
        elif "IT ACT" in act_upper:
            key = "IT_ACT"
        elif "CRPC" in act_upper:
            key = "CRPC"
        else:
            key = act_upper

        index[(key, section)] = entry
    return index


# Build index once at module load
_SECTION_INDEX = _build_section_index()


def lookup_section(act: str, section: str) -> dict:
    """Look up a legal section by act name and section number."""
    act_upper = act.upper()

    # Try to match act name to a key
    act_keys = []
    if "IPC" in act_upper or "INDIAN PENAL" in act_upper:
        act_keys = ["IPC"]
    elif "BNS" in act_upper and "BNSS" not in act_upper:
        act_keys = ["BNS"]
    elif "BNSS" in act_upper:
        act_keys = ["BNSS"]
    elif "ABKARI" in act_upper:
        act_keys = ["ABKARI"]
    elif "MV" in act_upper or "MOTOR" in act_upper:
        act_keys = ["MV_ACT"]
    elif "NDPS" in act_upper:
        act_keys = ["NDPS"]
    elif "POCSO" in act_upper:
        act_keys = ["POCSO"]
    elif "SC/ST" in act_upper or "POA" in act_upper:
        act_keys = ["SC_ST"]
    elif "ARMS" in act_upper:
        act_keys = ["ARMS"]
    elif "IT" in act_upper:
        act_keys = ["IT_ACT"]
    elif "CRPC" in act_upper:
        act_keys = ["CRPC"]
    else:
        # Try all keys
        act_keys = [act_upper]

    for key in act_keys:
        entry = _SECTION_INDEX.get((key, section))
        if not entry and "(" in section:
            # Fallback: remove parentheses (e.g., 318(4) -> 318)
            base_section = section.split("(")[0]
            entry = _SECTION_INDEX.get((key, base_section))
            
        if entry:
            return {
                "act": entry["act"],
                "section": entry["section"] if section == entry["section"] else f"{entry['section']} (matched from {section})",
                "description": entry.get("title", entry.get("description", "")),
                "offense_type": entry.get("crime_type", ""),
                "cognizable": entry.get("cognizable"),
                "bailable": entry.get("bailable"),
                "punishment": entry.get("punishment", ""),
            }

    return {"act": act, "section": section, "description": "Section details not found in local KB"}


def lookup_sections_batch(acts_list: list) -> list:
    """Look up multiple sections from an acts list like [{act, sections}]."""
    results = []
    for act_entry in acts_list:
        act_name = act_entry.get("act", "")
        for section in act_entry.get("sections", []):
            info = lookup_section(act_name, section)
            results.append(info)
    return results


def get_all_sections(act_filter: str = None) -> list:
    """Get all legal sections, optionally filtered by act."""
    results = []

    for entry in LEGAL_CORPUS:
        act_upper = entry["act"].upper()

        # Apply filter if specified
        if act_filter:
            filter_upper = act_filter.upper()
            if filter_upper not in act_upper:
                continue

        results.append({
            "act": entry["act"],
            "section": entry["section"],
            "description": entry.get("title", ""),
            "offense_type": entry.get("crime_type", ""),
            "cognizable": entry.get("cognizable"),
            "bailable": entry.get("bailable"),
            "punishment": entry.get("punishment", ""),
        })

    return results
