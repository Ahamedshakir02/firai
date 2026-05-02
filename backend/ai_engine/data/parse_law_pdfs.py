"""
Law PDF Parser — Extracts sections from IPC, BNS, and MV Act PDFs.
=================================================================
Parses the official law PDFs in backend/data/rules/ and generates
structured training data for the FirAI classifier.

Usage:
    python ai_engine/data/parse_law_pdfs.py

Output:
    ai_engine/data/datasets/law_sections.json — All extracted sections
"""

import os
import re
import sys
import json
import fitz  # PyMuPDF

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR = os.path.join(SCRIPT_DIR, "..", "..")
RULES_DIR = os.path.join(BACKEND_DIR, "data", "rules")
OUTPUT_DIR = os.path.join(SCRIPT_DIR, "datasets")

# ── Section → crime_type mapping (comprehensive) ──
# Maps section numbers to (crime_type, severity) for training labels

IPC_SECTION_MAP = {
    "302": ("murder", "critical"), "300": ("murder", "critical"),
    "301": ("murder", "critical"),
    "304": ("homicide", "critical"), "304A": ("death_by_negligence", "critical"),
    "304B": ("domestic_violence", "critical"),
    "306": ("abetment_of_suicide", "critical"),
    "307": ("assault", "critical"),  # attempt to murder
    "308": ("assault", "critical"),
    "323": ("assault", "medium"), "324": ("assault", "high"),
    "325": ("assault", "high"), "326": ("assault", "critical"),
    "326A": ("assault", "critical"), "326B": ("assault", "high"),
    "327": ("assault", "high"), "328": ("assault", "high"),
    "332": ("assault", "medium"), "333": ("assault", "high"),
    "334": ("assault", "medium"), "335": ("assault", "medium"),
    "336": ("rash_driving", "medium"), "337": ("rash_driving", "high"),
    "338": ("rash_driving", "critical"),
    "339": ("wrongful_restraint", "low"), "340": ("wrongful_confinement", "medium"),
    "341": ("wrongful_restraint", "low"), "342": ("wrongful_confinement", "medium"),
    "343": ("wrongful_confinement", "medium"), "344": ("wrongful_confinement", "high"),
    "345": ("wrongful_confinement", "high"), "346": ("wrongful_confinement", "high"),
    "347": ("wrongful_confinement", "high"), "348": ("wrongful_confinement", "high"),
    "349": ("assault", "low"), "350": ("assault", "low"),
    "351": ("assault", "low"), "352": ("assault", "low"),
    "353": ("assault", "medium"), "354": ("sexual_offense", "high"),
    "354A": ("sexual_offense", "high"), "354B": ("sexual_offense", "high"),
    "354C": ("sexual_offense", "high"), "354D": ("sexual_offense", "high"),
    "355": ("assault", "medium"), "356": ("assault", "medium"),
    "357": ("wrongful_confinement", "low"), "358": ("assault", "medium"),
    "359": ("kidnapping", "critical"), "360": ("kidnapping", "critical"),
    "361": ("kidnapping", "critical"), "362": ("kidnapping", "critical"),
    "363": ("kidnapping", "critical"), "363A": ("kidnapping", "critical"),
    "364": ("kidnapping", "critical"), "364A": ("kidnapping", "critical"),
    "365": ("kidnapping", "critical"), "366": ("kidnapping", "critical"),
    "366A": ("kidnapping", "critical"), "366B": ("kidnapping", "critical"),
    "367": ("kidnapping", "critical"), "368": ("kidnapping", "critical"),
    "369": ("kidnapping", "critical"),
    "370": ("kidnapping", "critical"), "371": ("kidnapping", "critical"),
    "372": ("sexual_offense", "critical"), "373": ("sexual_offense", "critical"),
    "375": ("sexual_offense", "critical"), "376": ("sexual_offense", "critical"),
    "376A": ("sexual_offense", "critical"), "376B": ("sexual_offense", "critical"),
    "376C": ("sexual_offense", "critical"), "376D": ("sexual_offense", "critical"),
    "377": ("sexual_offense", "critical"),
    "378": ("theft", "medium"), "379": ("theft", "medium"),
    "380": ("theft", "high"), "381": ("theft", "medium"),
    "382": ("theft", "high"),
    "383": ("extortion", "high"), "384": ("extortion", "high"),
    "385": ("extortion", "high"), "386": ("extortion", "high"),
    "387": ("extortion", "high"), "388": ("extortion", "high"),
    "389": ("extortion", "high"),
    "390": ("robbery", "high"), "391": ("dacoity", "critical"),
    "392": ("robbery", "high"), "393": ("robbery", "high"),
    "394": ("robbery", "critical"), "395": ("dacoity", "critical"),
    "396": ("dacoity", "critical"), "397": ("dacoity", "critical"),
    "398": ("dacoity", "critical"), "399": ("dacoity", "high"),
    "400": ("dacoity", "high"), "401": ("dacoity", "high"),
    "402": ("dacoity", "high"),
    "403": ("breach_of_trust", "medium"), "404": ("breach_of_trust", "medium"),
    "405": ("breach_of_trust", "medium"), "406": ("breach_of_trust", "medium"),
    "407": ("breach_of_trust", "high"), "408": ("breach_of_trust", "high"),
    "409": ("breach_of_trust", "high"),
    "410": ("stolen_property", "medium"), "411": ("stolen_property", "medium"),
    "412": ("stolen_property", "medium"), "413": ("stolen_property", "medium"),
    "414": ("stolen_property", "medium"),
    "415": ("cheating", "medium"), "416": ("cheating", "medium"),
    "417": ("cheating", "medium"), "418": ("cheating", "medium"),
    "419": ("cheating", "medium"), "420": ("cheating", "high"),
    "421": ("cheating", "medium"), "422": ("cheating", "medium"),
    "424": ("cheating", "medium"),
    "425": ("property_damage", "medium"), "426": ("property_damage", "medium"),
    "427": ("property_damage", "medium"), "428": ("property_damage", "medium"),
    "429": ("property_damage", "high"), "430": ("property_damage", "high"),
    "431": ("property_damage", "high"), "432": ("property_damage", "high"),
    "433": ("property_damage", "high"), "434": ("property_damage", "high"),
    "435": ("property_damage", "high"), "436": ("property_damage", "critical"),
    "437": ("property_damage", "critical"), "438": ("property_damage", "critical"),
    "440": ("property_damage", "high"),
    "441": ("trespass", "low"), "442": ("trespass", "medium"),
    "443": ("trespass", "medium"), "444": ("trespass", "medium"),
    "445": ("house_breaking", "high"), "446": ("house_breaking", "high"),
    "447": ("trespass", "low"), "448": ("trespass", "medium"),
    "449": ("house_breaking", "critical"), "450": ("house_breaking", "critical"),
    "451": ("house_breaking", "high"), "452": ("house_breaking", "high"),
    "453": ("house_breaking", "high"), "454": ("house_breaking", "high"),
    "455": ("house_breaking", "high"), "456": ("house_breaking", "high"),
    "457": ("house_breaking", "high"), "458": ("house_breaking", "critical"),
    "459": ("house_breaking", "high"), "460": ("house_breaking", "critical"),
    "461": ("house_breaking", "high"), "462": ("house_breaking", "high"),
    "463": ("forgery", "medium"), "464": ("forgery", "medium"),
    "465": ("forgery", "medium"), "466": ("forgery", "high"),
    "467": ("forgery", "high"), "468": ("forgery", "high"),
    "469": ("forgery", "high"), "470": ("forgery", "high"),
    "471": ("forgery", "medium"), "472": ("forgery", "medium"),
    "473": ("forgery", "medium"), "474": ("forgery", "medium"),
    "475": ("counterfeit", "high"), "476": ("counterfeit", "high"),
    "477": ("forgery", "medium"), "477A": ("forgery", "high"),
    "489A": ("counterfeit", "high"), "489B": ("counterfeit", "high"),
    "489C": ("counterfeit", "high"), "489D": ("counterfeit", "high"),
    "498A": ("domestic_violence", "high"),
    "499": ("criminal_intimidation", "medium"), "500": ("criminal_intimidation", "medium"),
    "503": ("criminal_intimidation", "high"), "504": ("criminal_intimidation", "medium"),
    "505": ("criminal_intimidation", "high"),
    "506": ("criminal_intimidation", "high"), "507": ("criminal_intimidation", "high"),
    "509": ("sexual_offense", "medium"),
    "511": ("other", "medium"),  # attempt
}

BNS_SECTION_MAP = {
    "100": ("murder", "critical"), "101": ("murder", "critical"),
    "103": ("murder", "critical"), "104": ("homicide", "critical"),
    "105": ("homicide", "critical"), "106": ("death_by_negligence", "critical"),
    "107": ("abetment_of_suicide", "critical"),
    "109": ("assault", "critical"),  # attempt to murder
    "115": ("assault", "medium"), "116": ("assault", "high"),
    "117": ("assault", "high"), "118": ("assault", "high"),
    "119": ("assault", "critical"), "120": ("assault", "high"),
    "121": ("assault", "medium"),
    "122": ("wrongful_restraint", "low"), "123": ("wrongful_confinement", "medium"),
    "124": ("wrongful_confinement", "high"),
    "125": ("rash_driving", "high"), "126": ("wrongful_restraint", "low"),
    "127": ("assault", "low"), "128": ("assault", "medium"),
    "129": ("assault", "low"), "130": ("assault", "medium"),
    "131": ("assault", "medium"), "132": ("assault", "medium"),
    "133": ("assault", "medium"),
    "135": ("sexual_offense", "critical"), "136": ("sexual_offense", "critical"),
    "137": ("sexual_offense", "high"),
    "140": ("kidnapping", "critical"), "141": ("kidnapping", "critical"),
    "142": ("kidnapping", "critical"), "143": ("kidnapping", "critical"),
    "144": ("kidnapping", "critical"),
    "303": ("theft", "medium"), "304": ("theft", "high"),
    "305": ("theft", "high"),
    "308": ("extortion", "high"), "309": ("robbery", "high"),
    "310": ("dacoity", "critical"), "311": ("dacoity", "critical"),
    "312": ("dacoity", "critical"),
    "316": ("breach_of_trust", "medium"), "317": ("breach_of_trust", "high"),
    "318": ("cheating", "medium"), "319": ("cheating", "high"),
    "323": ("property_damage", "medium"), "324": ("property_damage", "high"),
    "325": ("property_damage", "critical"),
    "329": ("trespass", "low"), "330": ("trespass", "medium"),
    "331": ("house_breaking", "high"), "332": ("house_breaking", "high"),
    "333": ("house_breaking", "high"),
    "336": ("forgery", "medium"), "337": ("forgery", "high"),
    "338": ("forgery", "high"), "339": ("forgery", "high"),
    "340": ("forgery", "high"),
    "351": ("criminal_intimidation", "high"),
    "356": ("criminal_intimidation", "medium"),
}

MV_SECTION_MAP = {
    "184": ("rash_driving", "high"),
    "185": ("drunk_driving", "high"),
    "186": ("drunk_driving", "medium"),
    "187": ("rash_driving", "high"),  # hit and run
    "188": ("rash_driving", "medium"),
    "189": ("rash_driving", "high"),
    "190": ("rash_driving", "medium"),
    "192": ("rash_driving", "medium"),
    "194": ("rash_driving", "medium"),
    "196": ("rash_driving", "medium"),
}


def extract_text_from_pdf(pdf_path: str) -> str:
    """Extract all text from a PDF."""
    doc = fitz.open(pdf_path)
    text = ""
    for page in doc:
        text += page.get_text() + "\n"
    doc.close()
    return text


def parse_ipc_sections(text: str) -> list:
    """Parse IPC sections from the full text."""
    return _parse_sections(text, "IPC", IPC_SECTION_MAP)


def parse_bns_sections(text: str) -> list:
    """Parse BNS sections from the full text."""
    return _parse_sections(text, "BNS", BNS_SECTION_MAP)


def parse_mv_sections(text: str) -> list:
    """Parse Motor Vehicle Act sections."""
    return _parse_sections(text, "Motor Vehicle Act", MV_SECTION_MAP)


def _parse_sections(text: str, act_name: str, section_map: dict) -> list:
    """
    Generic section parser for Indian legal texts.
    Extracts section number and its description text.
    """
    sections = []

    # Pattern: section number followed by period and text
    # Handles: "302. Punishment for murder..." or "103. Murder.—Whoever..."
    pattern = re.compile(
        r'(?:^|\n)\s*(\d+[A-Z]?)\.\s+'        # Section number (e.g., 302, 304A, 498A)
        r'(.+?)(?=\n\s*\d+[A-Z]?\.\s+|\Z)',    # Content until next section
        re.DOTALL
    )

    matches = pattern.findall(text)

    for sec_num, content in matches:
        sec_num = sec_num.strip()
        content = content.strip()

        # Skip very short content (likely noise)
        if len(content) < 30:
            continue

        # Get crime type mapping
        crime_info = section_map.get(sec_num)
        if not crime_info:
            continue  # Skip sections we can't classify

        crime_type, severity = crime_info

        # Extract title (first sentence or up to em-dash)
        title_match = re.match(r'(.+?)(?:\.\s*—|\.\s*\(|\.\s*$|—)', content)
        title = title_match.group(1).strip() if title_match else content[:80]
        title = re.sub(r'\s+', ' ', title)

        # Clean the description
        description = re.sub(r'\s+', ' ', content[:800]).strip()

        sections.append({
            "section": sec_num,
            "act": act_name,
            "title": title,
            "description": description,
            "crime_type": crime_type,
            "severity": severity,
            "source": "parsed_pdf",
        })

    return sections


def generate_training_data(parsed_sections: list) -> list:
    """
    Convert parsed sections into training examples for the BiLSTM classifier.
    Each section description becomes a training narrative.
    """
    training_data = []

    for section in parsed_sections:
        # Use full description as training narrative
        training_data.append({
            "narrative": section["description"],
            "crime_type": section["crime_type"],
            "severity": section["severity"],
            "source": f"law_pdf_{section['act']}_{section['section']}",
        })

        # Also create a shorter version from title
        if section.get("title") and len(section["title"]) > 10:
            training_data.append({
                "narrative": f"{section['title']}. Section {section['section']} of {section['act']}.",
                "crime_type": section["crime_type"],
                "severity": section["severity"],
                "source": f"law_pdf_title_{section['act']}_{section['section']}",
            })

    return training_data


def main():
    sys.stdout.reconfigure(encoding='utf-8')

    print("=" * 60)
    print("  FirAI — Law PDF Parser")
    print("  Extracting training data from IPC, BNS, MV Act PDFs")
    print("=" * 60)

    if not os.path.exists(RULES_DIR):
        print(f"[Error] Rules directory not found: {RULES_DIR}")
        return

    all_sections = []
    all_training = []

    # Map filenames to parsers
    pdf_configs = [
        ("repealedfileopen.pdf", "IPC", parse_ipc_sections),
        ("250883_english_01042024.pdf", "BNS", parse_bns_sections),
        ("a1988-59.pdf", "MV Act", parse_mv_sections),
    ]

    for filename, act_label, parser_fn in pdf_configs:
        filepath = os.path.join(RULES_DIR, filename)
        if not os.path.exists(filepath):
            print(f"[Skip] {filename} not found")
            continue

        print(f"\n[Parsing] {filename} ({act_label})...")
        text = extract_text_from_pdf(filepath)
        print(f"  Text length: {len(text):,} characters")

        sections = parser_fn(text)
        print(f"  Extracted: {sections_count} sections" if (sections_count := len(sections)) else "  No sections found")

        training = generate_training_data(sections)
        print(f"  Training examples: {len(training)}")

        all_sections.extend(sections)
        all_training.extend(training)

    # Also parse the updated BNS (a202345.pdf) if different
    bns_updated = os.path.join(RULES_DIR, "a202345.pdf")
    if os.path.exists(bns_updated):
        print(f"\n[Parsing] a202345.pdf (BNS 2025 updated)...")
        text = extract_text_from_pdf(bns_updated)
        sections = parse_bns_sections(text)
        # Only add sections not already covered
        existing_keys = {(s["act"], s["section"]) for s in all_sections}
        new_sections = [s for s in sections if (s["act"], s["section"]) not in existing_keys]
        print(f"  New sections (not in original): {len(new_sections)}")
        training = generate_training_data(new_sections)
        all_sections.extend(new_sections)
        all_training.extend(training)

    # Summary
    print(f"\n{'=' * 60}")
    print(f"  Total sections extracted: {len(all_sections)}")
    print(f"  Total training examples: {len(all_training)}")

    from collections import Counter
    crimes = Counter(t["crime_type"] for t in all_training)
    print(f"\n  Crime type distribution:")
    for ct, count in crimes.most_common():
        print(f"    {ct}: {count}")

    # Save
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    sections_path = os.path.join(OUTPUT_DIR, "law_sections.json")
    with open(sections_path, "w", encoding="utf-8") as f:
        json.dump(all_sections, f, indent=2, ensure_ascii=False)
    print(f"\n  Sections saved: {sections_path}")

    training_path = os.path.join(OUTPUT_DIR, "law_training_data.json")
    with open(training_path, "w", encoding="utf-8") as f:
        json.dump(all_training, f, indent=2, ensure_ascii=False)
    print(f"  Training data saved: {training_path}")


if __name__ == "__main__":
    main()
