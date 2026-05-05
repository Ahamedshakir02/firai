"""
Label Generator — Derives crime type & severity from IPC/BNS sections.
No Gemini needed. Labels come from the actual Indian law.
Also extracts sections from full_text when acts field is empty.
"""

import re
import os
import json
from collections import Counter

# ── IPC Section → (crime_type, severity) ──
IPC_MAP = {
    "302": ("murder", "critical"), "304": ("homicide", "critical"),
    "304A": ("death_by_negligence", "critical"),
    "306": ("abetment_of_suicide", "critical"),
    "307": ("attempt_to_murder", "critical"),
    "323": ("assault", "high"), "324": ("assault", "high"),
    "325": ("assault", "high"), "326": ("assault", "critical"),
    "341": ("wrongful_restraint", "low"), "342": ("wrongful_confinement", "medium"),
    "354": ("sexual_offense", "high"), "376": ("sexual_offense", "critical"),
    "379": ("theft", "medium"), "380": ("theft", "medium"),
    "381": ("theft", "medium"), "392": ("robbery", "high"),
    "395": ("dacoity", "critical"), "397": ("dacoity", "critical"),
    "406": ("breach_of_trust", "medium"), "409": ("breach_of_trust", "high"),
    "411": ("stolen_property", "medium"),
    "420": ("cheating", "medium"),
    "427": ("property_damage", "medium"),
    "447": ("trespass", "low"), "448": ("trespass", "medium"),
    "457": ("house_breaking", "high"),
    "465": ("forgery", "medium"), "467": ("forgery", "high"),
    "468": ("forgery", "medium"), "471": ("forgery", "medium"),
    "498A": ("domestic_violence", "high"),
    "506": ("criminal_intimidation", "high"),
    "279": ("rash_driving", "high"),
    "294": ("public_nuisance", "low"), "294(b)": ("public_nuisance", "low"),
    "363": ("kidnapping", "critical"), "366": ("kidnapping", "critical"),
    "489A": ("counterfeit", "high"),
    "34": (None, None), "3": (None, None),  # modifiers
}

# ── BNS Section → (crime_type, severity) ──
BNS_MAP = {
    "100": ("murder", "critical"), "103": ("murder", "critical"),
    "104": ("murder", "critical"),
    "105": ("homicide", "critical"), "106": ("death_by_negligence", "critical"),
    "108": ("abetment_of_suicide", "critical"),
    "109": ("attempt_to_murder", "critical"),
    "115": ("assault", "high"), "115(2)": ("assault", "high"),
    "117": ("assault", "critical"),
    "118": ("assault", "high"), "118(1)": ("assault", "high"), "118(2)": ("assault", "high"),
    "118(a)": ("assault", "high"),
    "119": ("assault", "high"),
    "121": ("assault", "medium"),
    "122": ("assault", "medium"),
    "125": ("rash_driving", "high"), "125(a)": ("rash_driving", "high"), "125(b)": ("rash_driving", "high"),
    "126": ("wrongful_restraint", "low"), "126(2)": ("wrongful_confinement", "medium"),
    "127": ("wrongful_confinement", "medium"),
    "131": ("assault", "medium"),
    "132": ("assault", "high"),
    "137": ("kidnapping", "critical"), "140": ("kidnapping", "critical"),
    "151": ("criminal_intimidation", "high"),
    "189": ("public_servant_offense", "medium"), "189(2)": ("public_servant_offense", "medium"),
    "190": ("public_servant_offense", "medium"),
    "191": ("public_servant_offense", "medium"), "191(2)": ("public_servant_offense", "medium"),
    "22": ("unnatural_death", "critical"),  # BNS 22 — acts done by several persons in furtherance of common intent (procedural, but indicates a group crime)
    "57": ("abetment_of_suicide", "critical"),  # BNS 57 — abetment of a thing
    "61": ("criminal_conspiracy", "high"),
    "63": ("sexual_offense", "critical"), "64": ("sexual_offense", "critical"),
    "65": ("sexual_offense", "critical"),
    "74": ("sexual_offense", "high"), "75": ("sexual_offense", "high"),
    "76": ("assault", "high"),  # BNS 76 — voluntarily causing hurt
    "77": ("assault", "high"),
    "78": ("assault", "critical"),  # grievous hurt
    "85": ("domestic_violence", "high"),  # BNS 85 — cruelty by husband
    "281": ("rash_driving", "high"),
    "303": ("theft", "medium"), "303(2)": ("theft", "medium"),
    "304": ("theft", "high"),
    "305": ("theft", "high"),  # theft by servant
    "308": ("extortion", "high"), "309": ("robbery", "high"),
    "310": ("dacoity", "critical"),
    "316": ("breach_of_trust", "medium"), "316(2)": ("breach_of_trust", "high"),
    "318": ("cheating", "medium"), "318(4)": ("cheating", "high"),
    "319": ("cheating", "medium"),
    "324": ("property_damage", "medium"), "324(2)": ("property_damage", "high"),
    "329": ("trespass", "low"), "329(3)": ("trespass", "medium"), "329(4)": ("trespass", "medium"),
    "331": ("house_breaking", "high"),
    "332": ("house_breaking", "high"), "332(0)": ("house_breaking", "high"),
    "336": ("forgery", "medium"), "338": ("forgery", "high"),
    "351": ("criminal_intimidation", "high"),
    "352": ("criminal_intimidation", "medium"),
    "3(5)": (None, None), "3": (None, None),  # general modifiers
}

# ── Special Acts ──
SPECIAL_ACT_PATTERNS = [
    (r"(?:Motor Vehicle|MV)\s*Act.*?(\d+)", {
        "185": ("drunk_driving", "high"),
        "184": ("rash_driving", "high"),
        "485": ("drunk_driving", "high"),
    }),
    (r"(?:Abkari|ABKARI|Kerala Abkari)\s*Act.*?(\d+)", {
        "55": ("excise_offense", "medium"),
        "15": ("excise_offense", "medium"),
    }),
    (r"(?:NDPS)\s*Act.*?(\d+)", {
        "4": ("drug_offense", "high"),
        "8": ("drug_offense", "high"),
        "20": ("drug_offense", "high"),
        "21": ("drug_offense", "high"),
        "22": ("drug_offense", "high"),
        "27": ("drug_offense", "medium"),
        "27(b)": ("drug_offense", "medium"),
    }),
    (r"(?:POCSO).*?(\d+)", {
        "4": ("sexual_offense", "critical"),
        "6": ("sexual_offense", "critical"),
        "8": ("sexual_offense", "critical"),
        "10": ("sexual_offense", "critical"),
        "12": ("sexual_offense", "high"),
    }),
    (r"PDPP\s*ACT", {
        "_any": ("property_damage", "medium"),
    }),
]

# ── BNSS (procedural code) sections — not crimes, but indicate case type ──
BNSS_INDICATOR = {
    "194": ("unnatural_death", "critical"),  # BNSS 194 = inquest for unnatural death
    "173": (None, None),  # FIR registration section
}

# Severity ranking
SEVERITY_RANK = {"low": 0, "medium": 1, "high": 2, "critical": 3}


def _extract_sections_from_fulltext(full_text: str) -> list:
    """
    Extract IPC/BNS/Special Act sections from the full FIR text.
    Looks for patterns like 'U/S 303(2) of BNS', 'U/s 15(c) of KERALA ABKARI ACT'.
    """
    if not full_text:
        return []

    results = []

    # Pattern: U/S <sections> <act>
    us_matches = re.findall(
        r'U/[Ss]\s+(.+?)(?:\s+ആയി|\s+aya\b)',
        full_text, re.IGNORECASE
    )

    for match in us_matches:
        match = match.strip()

        # Determine act type
        act_name = "UNKNOWN"
        if re.search(r'\bBNS\b', match, re.IGNORECASE):
            act_name = "BNS"
        elif re.search(r'\bIPC\b', match, re.IGNORECASE):
            act_name = "IPC"
        elif re.search(r'\bBNSS\b', match, re.IGNORECASE):
            act_name = "BNSS"
        elif re.search(r'Abkari\s*Act', match, re.IGNORECASE):
            act_name = "ABKARI"
        elif re.search(r'MV\s*Act|Motor\s*Vehicle', match, re.IGNORECASE):
            act_name = "MV_ACT"
        elif re.search(r'PDPP', match, re.IGNORECASE):
            act_name = "PDPP"

        # Extract section numbers
        sections = re.findall(r'(\d+(?:\s*\([^)]*\))?)', match)
        sections = [s.replace(' ', '') for s in sections]

        if sections:
            results.append({"act": act_name, "sections": sections})

    return results


def derive_labels(acts_list: list, full_text: str = "") -> dict:
    """
    Derive crime_type and severity from acts list.
    Falls back to extracting from full_text if acts_list is empty.
    """
    # If acts is empty, try extracting from full_text
    if not acts_list and full_text:
        acts_list = _extract_sections_from_fulltext(full_text)

    if not acts_list:
        return {"crime_type": "other", "severity": "medium", "all_crimes": [], "extracted_acts": []}

    found_crimes = []

    for act_entry in acts_list:
        act_name = act_entry.get("act", "")
        sections = act_entry.get("sections", [])
        act_upper = act_name.upper()

        for section in sections:
            section = str(section).strip()
            crime_type, severity = None, None

            if "IPC" in act_upper or "INDIAN PENAL" in act_upper:
                crime_type, severity = IPC_MAP.get(section, (None, None))

            elif "BNS" in act_upper or "BHARATIYA" in act_upper or "NYAYA" in act_upper:
                crime_type, severity = BNS_MAP.get(section, (None, None))

            elif "BNSS" in act_upper:
                crime_type, severity = BNSS_INDICATOR.get(section, (None, None))

            elif "ABKARI" in act_upper:
                section_num = re.match(r'(\d+)', section)
                if section_num:
                    for _, sec_map in SPECIAL_ACT_PATTERNS:
                        result = sec_map.get(section_num.group(1))
                        if result:
                            crime_type, severity = result
                            break

            elif "MV" in act_upper or "MOTOR" in act_upper:
                section_num = re.match(r'(\d+)', section)
                if section_num:
                    for _, sec_map in SPECIAL_ACT_PATTERNS:
                        result = sec_map.get(section_num.group(1))
                        if result:
                            crime_type, severity = result
                            break

            elif "NDPS" in act_upper:
                # NDPS Act sections
                section_num = re.match(r'(\d+)', section)
                if section_num:
                    ndps_map = {"4": ("drug_offense", "high"), "8": ("drug_offense", "high"),
                                "20": ("drug_offense", "high"), "21": ("drug_offense", "high"),
                                "22": ("drug_offense", "high"), "27": ("drug_offense", "medium")}
                    result = ndps_map.get(section_num.group(1))
                    if result:
                        crime_type, severity = result

            elif "POCSO" in act_upper:
                section_num = re.match(r'(\d+)', section)
                if section_num:
                    pocso_map = {"4": ("sexual_offense", "critical"), "6": ("sexual_offense", "critical"),
                                 "8": ("sexual_offense", "critical"), "10": ("sexual_offense", "critical"),
                                 "12": ("sexual_offense", "high")}
                    result = pocso_map.get(section_num.group(1))
                    if result:
                        crime_type, severity = result

            if crime_type:
                found_crimes.append({"crime_type": crime_type, "severity": severity, "section": section, "act": act_name})

    if not found_crimes:
        return {"crime_type": "other", "severity": "medium", "all_crimes": [], "extracted_acts": acts_list}

    # Primary crime = highest severity
    found_crimes.sort(key=lambda x: SEVERITY_RANK.get(x["severity"], 1), reverse=True)
    primary = found_crimes[0]

    return {
        "crime_type": primary["crime_type"],
        "severity": primary["severity"],
        "all_crimes": found_crimes,
        "extracted_acts": acts_list,
    }


def generate_labels_from_structured_firs(structured_dir: str) -> list:
    """
    Read all structured FIR JSONs and generate training labels.
    Uses both acts field AND full_text for section extraction.
    """
    labeled = []
    for fname in sorted(os.listdir(structured_dir)):
        if not fname.endswith(".json"):
            continue
        fpath = os.path.join(structured_dir, fname)
        with open(fpath, "r", encoding="utf-8") as f:
            data = json.load(f)

        narrative = data.get("narrative", "").strip()
        if not narrative:
            continue

        labels = derive_labels(
            data.get("acts", []),
            data.get("full_text", "")
        )

        labeled.append({
            "file": fname,
            "narrative": narrative,
            "crime_type": labels["crime_type"],
            "severity": labels["severity"],
            "all_crimes": labels["all_crimes"],
            "acts": data.get("acts", []),
            "extracted_acts": labels.get("extracted_acts", []),
            "place": data.get("place", ""),
            "accused": data.get("accused", []),
            "complainant": data.get("complainant", {}),
        })

    print(f"[LabelGenerator] Generated labels for {len(labeled)} FIRs")
    return labeled


if __name__ == "__main__":
    import sys
    sys.stdout.reconfigure(encoding='utf-8')

    structured_dir = os.path.join(os.path.dirname(__file__), "..", "..", "data", "structured")
    labeled = generate_labels_from_structured_firs(structured_dir)

    # Print summary
    crimes = Counter(d["crime_type"] for d in labeled)
    print("\nCrime type distribution:")
    for ct, count in crimes.most_common():
        print(f"  {ct}: {count}")

    # Show each FIR's label
    print("\nPer-FIR labels:")
    for d in labeled:
        print(f"  {d['file']}: {d['crime_type']} ({d['severity']})")

    # Save labeled data
    out_dir = os.path.join(os.path.dirname(__file__), "datasets")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "labeled_firs.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(labeled, f, indent=2, ensure_ascii=False)
    print(f"\nSaved to {out_path}")
