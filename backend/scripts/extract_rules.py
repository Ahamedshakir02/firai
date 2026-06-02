import re
import json
from pathlib import Path

try:
    import fitz
except ImportError:
    raise SystemExit("PyMuPDF is required: pip install pymupdf")

SCRIPT_DIR = Path(__file__).parent
RULES_DIR = SCRIPT_DIR.parent / "data" / "rules"

# Skip the first N pages to avoid picking up Table of Contents entries
_TOC_SKIP_PAGES = 10

# Map PDF filenames → Act names
_PDF_FILES = {
    "repealedfileopen.pdf": "IPC",
    "a202345.pdf": "BNS",
    "a1988-59.pdf": "MVA",
}

_SECTION_PATTERN = re.compile(r'^(\d+[a-zA-Z]?)\.\s+(.*)')


def extract_sections(pdf_path: Path, act_name: str) -> list:
    print(f"Extracting sections from {pdf_path.name} ({act_name})...")
    try:
        doc = fitz.open(str(pdf_path))
    except Exception as e:
        print(f"  ERROR: Could not open {pdf_path.name}: {e}")
        return []

    # Combine text from pages after the ToC
    body_text = ""
    for page_index, page in enumerate(doc):
        if page_index < _TOC_SKIP_PAGES:
            continue
        body_text += page.get_text("text") + "\n"
    doc.close()

    sections = []
    current_section = None
    current_text = []

    for line in body_text.split("\n"):
        line = line.strip()
        if not line:
            continue

        match = _SECTION_PATTERN.match(line)
        if match:
            if current_section:
                sections.append({
                    "act": act_name,
                    "section": current_section["num"],
                    "title": current_section["title"],
                    "description": "\n".join(current_text).strip(),
                })

            sec_num = match.group(1)
            title = match.group(2)

            desc_start = ""
            if ".—" in title:
                title, desc_start = title.split(".—", 1)
            elif "—" in title:
                title, desc_start = title.split("—", 1)

            current_section = {"num": sec_num, "title": title.strip()}
            current_text = [desc_start] if desc_start else []
        elif current_section:
            current_text.append(line)

    if current_section:
        sections.append({
            "act": act_name,
            "section": current_section["num"],
            "title": current_section["title"],
            "description": "\n".join(current_text).strip(),
        })

    print(f"  Extracted {len(sections)} sections from {act_name}")
    return sections


def main():
    output_file = RULES_DIR / "extracted_rules.json"
    all_sections = []

    for filename, act_name in _PDF_FILES.items():
        pdf_path = RULES_DIR / filename
        if not pdf_path.exists():
            print(f"File not found, skipping: {pdf_path}")
            continue
        sections = extract_sections(pdf_path, act_name)
        if sections:
            all_sections.append({"act": act_name, "sections": sections})

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(all_sections, f, indent=2)

    total = sum(len(a["sections"]) for a in all_sections)
    print(f"\nSaved {total} total sections to {output_file}")


if __name__ == "__main__":
    main()
