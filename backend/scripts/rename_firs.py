"""
FirAI — Rename FIR files to their actual FIR numbers.
=====================================================
Renames files like 1.json → FIR_0517_2024_KALPAKANCHERRY.json
and corresponding 1.pdf → FIR_0517_2024_KALPAKANCHERRY.pdf

Also updates the "file" field inside each JSON to match the new name.

Usage:
  python scripts/rename_firs.py              # Dry run (preview only)
  python scripts/rename_firs.py --apply      # Actually rename files
"""

import os
import sys
import re
import json

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR = os.path.join(SCRIPT_DIR, "..")
STRUCTURED_DIR = os.path.join(BACKEND_DIR, "data", "structured")
RAW_PDF_DIR = os.path.join(BACKEND_DIR, "data", "raw_pdfs")


def extract_fir_info(full_text: str) -> dict:
    """
    Extract FIR number, year, and police station from full_text.
    Looks for patterns like:
      - FIR No.(പ്രഥമ വിവര നമ്പര്‍) : 0517  Year (വര്‍ഷം) : 2024
      - FIR No (പ്രഥമ വിവര നമ്പര്‍) : 0517 / 2024
      - PS (പോലീസ് സ്റ്റേഷന്‍) : KALPAKANCHERRY
    """
    info = {"fir_number": None, "year": None, "station": None}

    if not full_text:
        return info

    # Pattern 1: FIR No ... : NNNN / YYYY
    fir_match = re.search(
        r'FIR\s*(?:No\.?|൦\.?)\s*\(.*?\)\s*:\s*(\d{3,5})\s*/?\s*(\d{4})?',
        full_text, re.IGNORECASE
    )
    if fir_match:
        info["fir_number"] = fir_match.group(1)
        if fir_match.group(2):
            info["year"] = fir_match.group(2)

    # If year not found in FIR No line, look for Year field
    if not info["year"]:
        year_match = re.search(
            r'Year\s*\(.*?\)\s*:\s*(\d{4})',
            full_text, re.IGNORECASE
        )
        if year_match:
            info["year"] = year_match.group(1)

    # Extract police station
    ps_match = re.search(
        r'PS\s*\(.*?\)\s*:\s*([A-Z][A-Z\s]+?)(?:\s*FIR|\s*$|\n)',
        full_text, re.IGNORECASE
    )
    if ps_match:
        info["station"] = ps_match.group(1).strip()

    return info


def generate_new_name(info: dict, old_stem: str) -> str:
    """Generate a new filename from extracted FIR info."""
    fir_num = info.get("fir_number")
    year = info.get("year")
    station = info.get("station")

    if not fir_num:
        return None  # Can't rename without FIR number

    parts = ["FIR", fir_num]
    if year:
        parts.append(year)
    if station:
        # Clean station name for filename
        clean_station = re.sub(r'[^A-Za-z0-9]', '_', station)
        clean_station = re.sub(r'_+', '_', clean_station).strip('_')
        parts.append(clean_station)

    return "_".join(parts)


def main():
    apply = "--apply" in sys.argv

    if apply:
        print("=" * 60)
        print("  MODE: APPLY — Files WILL be renamed")
        print("=" * 60)
    else:
        print("=" * 60)
        print("  MODE: DRY RUN — Preview only (use --apply to rename)")
        print("=" * 60)

    json_files = sorted(
        [f for f in os.listdir(STRUCTURED_DIR) if f.endswith(".json")],
        key=lambda x: int(re.match(r'(\d+)', x).group(1)) if re.match(r'(\d+)', x) else 0
    )

    renames = []
    errors = []

    print(f"\nScanning {len(json_files)} JSON files...\n")

    for fname in json_files:
        fpath = os.path.join(STRUCTURED_DIR, fname)
        stem = os.path.splitext(fname)[0]

        with open(fpath, "r", encoding="utf-8") as f:
            data = json.load(f)

        full_text = data.get("full_text", "")
        info = extract_fir_info(full_text)
        new_stem = generate_new_name(info, stem)

        if not new_stem:
            errors.append(f"  ✗ {fname} — Could not extract FIR number")
            continue

        # Check for duplicates
        existing = [r for r in renames if r["new_stem"] == new_stem]
        if existing:
            new_stem = f"{new_stem}_{stem}"  # Append old number to disambiguate

        pdf_name = f"{stem}.pdf"
        pdf_exists = os.path.exists(os.path.join(RAW_PDF_DIR, pdf_name))

        renames.append({
            "old_stem": stem,
            "new_stem": new_stem,
            "json_old": fname,
            "json_new": f"{new_stem}.json",
            "pdf_old": pdf_name if pdf_exists else None,
            "pdf_new": f"{new_stem}.pdf" if pdf_exists else None,
            "info": info,
            "data": data,
        })

        station = info.get("station", "???")
        print(f"  {fname:12s} → {new_stem}.json  (FIR {info['fir_number']}/{info['year']} @ {station})")
        if pdf_exists:
            print(f"  {pdf_name:12s} → {new_stem}.pdf")

    if errors:
        print(f"\nErrors ({len(errors)}):")
        for e in errors:
            print(e)

    print(f"\nSummary: {len(renames)} files to rename, {len(errors)} errors")

    if not apply:
        print("\nRun with --apply to actually rename files.")
        return

    # Apply renames
    print("\nApplying renames...")
    for r in renames:
        # Rename JSON
        old_json = os.path.join(STRUCTURED_DIR, r["json_old"])
        new_json = os.path.join(STRUCTURED_DIR, r["json_new"])

        # Update the "file" field inside JSON
        r["data"]["file"] = r["json_new"]
        # Add fir_number_extracted field for reference
        r["data"]["fir_number_extracted"] = f"{r['info']['fir_number']}/{r['info']['year']}"
        r["data"]["police_station"] = r["info"].get("station", "")
        # Also keep old filename for reference
        r["data"]["original_file"] = r["json_old"]

        with open(old_json, "w", encoding="utf-8") as f:
            json.dump(r["data"], f, indent=2, ensure_ascii=False)

        os.rename(old_json, new_json)
        print(f"  ✓ {r['json_old']} → {r['json_new']}")

        # Rename PDF
        if r["pdf_old"]:
            old_pdf = os.path.join(RAW_PDF_DIR, r["pdf_old"])
            new_pdf = os.path.join(RAW_PDF_DIR, r["pdf_new"])
            os.rename(old_pdf, new_pdf)
            print(f"  ✓ {r['pdf_old']} → {r['pdf_new']}")

    print(f"\n✅ Done! Renamed {len(renames)} file pairs.")


if __name__ == "__main__":
    main()
