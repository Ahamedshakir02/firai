"""
FIR Processor Service
---------------------
Handles PDF upload, OCR text extraction, text cleaning,
and narrative extraction from FIR documents.

Supports narratives in both Malayalam and English.
"""

import os
import re
import io
import json
import tempfile
import fitz  # PyMuPDF
import pytesseract
from PIL import Image
from typing import Optional


def extract_text_from_pdf(pdf_path: str) -> str:
    """Extract text from FIR PDF using OCR (supports Malayalam + English)."""
    doc = fitz.open(pdf_path)
    full_text = ""

    for page_number in range(len(doc)):
        page = doc[page_number]
        # 200 DPI is sufficient for quality printed FIRs and ~40% faster than 300 DPI
        pix = page.get_pixmap(dpi=200)
        img = Image.open(io.BytesIO(pix.tobytes("png")))

        text = pytesseract.image_to_string(
            img,
            lang="mal+eng",
            config="--oem 3 --psm 6"
        )
        full_text += text + "\n"

    doc.close()
    return full_text


def clean_text(text: str) -> str:
    """Clean OCR-extracted text: remove noise, normalize whitespace."""
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text)
    # Remove page numbers
    text = re.sub(r'Page\s*\d+', '', text, flags=re.IGNORECASE)
    return text.strip()


def extract_narrative(text: str) -> Optional[str]:
    """
    Extract the narrative section (Section 12 - First Information Contents)
    from the full FIR text.

    The narrative is the core content - can be in Malayalam or English.
    """
    narrative = None

    # Primary pattern: Section 12 to Section 13
    match = re.search(
        r'First Information Contents.*?\n(.*?)\n\s*13\.',
        text,
        flags=re.IGNORECASE | re.DOTALL
    )

    if not match:
        # Fallback: Malayalam pattern
        match = re.search(
            r'First Information Contents.*?(.*?)Directed to take up the Investigation',
            text,
            flags=re.IGNORECASE | re.DOTALL
        )

    if not match:
        # Fallback: using Malayalam section header
        match = re.search(
            r'എഫ്\u200c\.ഐ\.ആര്\u200d ഉള്ളടക്കം.*?\n(.*?)\n\s*13\.',
            text,
            flags=re.IGNORECASE | re.DOTALL
        )

    if match:
        narrative = match.group(1).strip()

        # Remove Malayalam FIR header inside brackets
        narrative = re.sub(
            r'\(.*?ഉള്ളടക്കം.*?\)',
            '',
            narrative,
            flags=re.IGNORECASE
        )

        # Remove "Action taken" section leakage
        narrative = re.sub(
            r'13\..*',
            '',
            narrative,
            flags=re.IGNORECASE | re.DOTALL
        )

        # Normalize whitespace
        narrative = re.sub(r'\s+', ' ', narrative).strip()

    return narrative


def extract_date(text: str) -> Optional[str]:
    """Extract date from FIR text."""
    match = re.search(r'\b\d{2}[/-]\d{2}[/-]\d{4}\b', text)
    return match.group(0) if match else None


def extract_fir_number(text: str) -> Optional[str]:
    """
    Extract the Kerala Police CCTNS FIR number from full text.
    Matches patterns like: 'FIR No. : 0017 / 2025' or 'FIR No (പ്രഥമ വിവര നമ്പർ) : 0017 / 2025'
    Returns normalized format: '0017/2025'
    """
    # Pattern: FIR No followed by optional Malayalam text, colon, number / year
    patterns = [
        r'FIR\s*No[^:]*:\s*(\d+)\s*/\s*(\d{4})',                   # FIR No. : 0017 / 2025
        r'FIR\s*No\.\s*\(.*?\)\s*:\s*(\d+)\s*/\s*(\d{4})',         # FIR No (Malayalam) : 0017 / 2025
        r'Crime\s*No[^:]*:\s*(\d+)\s*/\s*(\d{4})',                  # Crime No. : ...
        r'Case\s*No[^:]*:\s*(\d+)\s*/\s*(\d{4})',                   # Case No. : ...
        r'Cr\.\s*No[^:]*:\s*(\d+)\s*/\s*(\d{4})',                   # Cr. No. : ...
        r'\bCrime\b.*?(\d{4})\s*/\s*(\d{4})',                        # fallback
    ]
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            num, year = match.group(1), match.group(2)
            return f"{num.zfill(4)}/{year}"
    return None


def extract_acts(text: str) -> list:
    """Extract acts and sections from FIR text."""
    acts = []
    lines = text.split("\n")

    for i, line in enumerate(lines):
        if re.search(r'Acts\s*\(.*?\)\s*Sections', line, re.IGNORECASE):
            j = i + 1
            while j < len(lines):
                row = lines[j].strip()
                if not row or re.search(r'Day\s*\(|Date\s*From|Occurrence of Offence', row, re.IGNORECASE):
                    break

                match = re.match(
                    r'([A-Za-z\s\.\(\)0-9]+?)\s+([0-9,\(\)a-zA-Z\s]+)',
                    row
                )
                if match:
                    act_name = match.group(1).strip()
                    section_part = match.group(2)
                    raw_sections = re.findall(r'\b\d+(?:\([a-zA-Z]+\))?', section_part)

                    sections = []
                    for s in raw_sections:
                        num = int(re.match(r'\d+', s).group())
                        if num < 1000:
                            sections.append(s)

                    if sections:
                        acts.append({"act": act_name, "sections": list(dict.fromkeys(sections))})
                j += 1
            break

    # Fallback: inline extraction
    if not acts:
        inline_patterns = re.findall(
            r'\b(IPC\s*1860|THE\s+BHARATIYA\s+NYAYA\s+SANHITA\s*\(BNS\)|BNS|Motor Vehicle Act\s*\d{4})\s+([0-9,\(\)a-zA-Z\s]+)',
            text,
            re.IGNORECASE
        )
        for act_name, section_part in inline_patterns:
            sections = []
            for s in re.findall(r'\b\d+(?:\([a-zA-Z]+\))?', section_part):
                if int(re.match(r'\d+', s).group()) < 1000:
                    sections.append(s)
            if sections:
                acts.append({"act": act_name.strip(), "sections": list(dict.fromkeys(sections))})

    # Normalize act names
    normalized = []
    for a in acts:
        act_upper = a["act"].upper()
        if "MOTOR" in act_upper:
            act_std = "Motor Vehicle Act 1988"
        elif "BNS" in act_upper or "BHARATIYA NYAYA SANHITA" in act_upper:
            act_std = "Bharatiya Nyaya Sanhita (BNS)"
        elif "IPC" in act_upper:
            act_std = "Indian Penal Code (IPC)"
        else:
            act_std = a["act"]
        normalized.append({"act": act_std, "sections": a["sections"]})

    return normalized


def extract_complainant(text: str) -> dict:
    """Extract complainant details from FIR text."""
    complainant = {"name": None, "father_name": None, "dob": None}

    name_match = re.search(
        r'\(a\)\.?\s*Name.*?([A-Z]{3,}(?:\s+[A-Z]{2,})?)',
        text, flags=re.IGNORECASE | re.DOTALL
    )

    father_match = re.search(
        r"Father's\s*/?\s*Mother's\s*/?\s*Husband's\s*Name.*?([A-Z\s]{3,40})",
        text, flags=re.IGNORECASE | re.DOTALL
    )

    if name_match:
        complainant["name"] = name_match.group(1).strip().upper()

    if father_match:
        candidate = father_match.group(1).strip().upper()
        invalid = ["DISTRICT", "KERALA", "INDIA", "MALAPPURAM", "ADDRESS", "PRESENT", "PERMANENT"]
        if not any(w in candidate for w in invalid):
            complainant["father_name"] = candidate

    return complainant


def extract_accused(text: str) -> list:
    """Extract accused persons from FIR text."""
    accused = []

    section_match = re.search(
        r'Details of known.*?accused with full particulars(.*?)(Reason for delay|Particulars of properties|$)',
        text, flags=re.IGNORECASE | re.DOTALL
    )
    accused_text = section_match.group(1) if section_match else ""

    pattern = re.compile(r'([A-Z][A-Z\s\.]{2,50})\s+Age[-\s]*([0-9]{1,3})', re.IGNORECASE)
    seen = set()

    for match in pattern.finditer(accused_text):
        name = match.group(1).strip().upper()
        if name not in seen:
            seen.add(name)
            accused.append({
                "name": name,
                "father_name": None,
                "dob": None,
                "address": None
            })

    return accused


def extract_place(text: str) -> Optional[str]:
    """Extract place/location from FIR text."""
    match = re.search(
        r'Location\s*/\s*Address.*?([A-Za-z][A-Za-z\s]{3,60})',
        text, flags=re.IGNORECASE
    )
    if match:
        return re.sub(r'\s+', ' ', match.group(1)).strip()
    return None


def extract_district_and_station(text: str) -> tuple:
    """Extract district and police station from FIR text."""
    district = None
    station = None

    d_match = re.search(r'District.*?:\s*([A-Z]+)', text, re.IGNORECASE)
    s_match = re.search(r'PS\s*\(.*?\)\s*:\s*([A-Z]+)', text, re.IGNORECASE)

    if d_match:
        district = d_match.group(1).strip()
    if s_match:
        station = s_match.group(1).strip()

    return district, station


def process_fir_pdf(pdf_path: str) -> dict:
    """
    Complete FIR processing pipeline:
    PDF → OCR → Clean → Extract all fields → Return structured data.

    The narrative is the core output.
    """
    # Step 1: Extract raw text via OCR
    raw_text = extract_text_from_pdf(pdf_path)

    # Step 2: Clean the text
    cleaned_text = clean_text(raw_text)

    # Step 3: Extract the narrative (the core)
    narrative = extract_narrative(cleaned_text)

    # Step 4: Extract metadata fields
    fir_number = extract_fir_number(cleaned_text) or extract_fir_number(raw_text)
    fir_date = extract_date(cleaned_text)
    acts = extract_acts(raw_text)  # Use raw text for table parsing
    place = extract_place(cleaned_text)
    complainant = extract_complainant(cleaned_text)
    accused = extract_accused(cleaned_text)
    district, station = extract_district_and_station(cleaned_text)

    return {
        "narrative": narrative or cleaned_text[:1000],  # Fallback to first 1000 chars
        "full_text": cleaned_text,
        "fir_number": fir_number,
        "fir_date": fir_date,
        "acts": acts,
        "place": place,
        "complainant": complainant,
        "accused": accused,
        "district": district,
        "police_station": station,
    }


def process_fir_text(text: str) -> dict:
    """
    Process a raw FIR text (already extracted/pasted).
    Supports both Malayalam and English narratives.
    """
    cleaned = clean_text(text)
    narrative = extract_narrative(cleaned)

    return {
        "narrative": narrative or cleaned[:1000],
        "full_text": cleaned,
        "fir_number": extract_fir_number(cleaned),
        "fir_date": extract_date(cleaned),
        "acts": extract_acts(text),
        "place": extract_place(cleaned),
        "complainant": extract_complainant(cleaned),
        "accused": extract_accused(cleaned),
        "district": None,
        "police_station": None,
    }


def generate_fir_filename(
    fir_number: Optional[str] = None,
    police_station: Optional[str] = None,
    fallback_name: Optional[str] = None,
    extension: str = ".pdf",
) -> str:
    """
    Generate a standardized FIR filename from extracted metadata.

    Examples:
        fir_number='0517/2024', station='KALPAKANCHERRY' → 'FIR_0517_2024_KALPAKANCHERRY.pdf'
        fir_number='0017/2025', station='KOTTAKKAL'      → 'FIR_0017_2025_KOTTAKKAL.pdf'
        fir_number=None, fallback_name='upload.pdf'      → 'upload.pdf'  (unchanged)
    """
    if not fir_number:
        return fallback_name or f"FIR_unknown{extension}"

    # Split '0517/2024' → ['0517', '2024']
    parts = ["FIR"]
    for p in re.split(r'[/\\-]', fir_number):
        p = p.strip()
        if p:
            parts.append(p)

    # Append police station (sanitized for filenames)
    if police_station:
        clean_station = re.sub(r'[^A-Za-z0-9]', '_', police_station.strip())
        clean_station = re.sub(r'_+', '_', clean_station).strip('_')
        if clean_station:
            parts.append(clean_station)

    stem = "_".join(parts)
    return f"{stem}{extension}"
