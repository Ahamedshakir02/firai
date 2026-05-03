"""
FirAI — Reprocess All FIR PDFs
===============================
Deletes all existing structured JSONs, removes duplicate PDFs,
and re-processes every unique PDF through the current fir_processor
pipeline for clean, consistent data.

Features:
  - Detects and removes duplicate PDFs (same file size + content hash)
  - Renames ugly hash-named PDFs to proper FIR names
  - Extracts ALL fields: fir_number, district, station, acts, accused, narrative
  - Skips non-FIR PDFs gracefully

Usage:
  python scripts/reprocess_all_firs.py              # Dry run (preview only)
  python scripts/reprocess_all_firs.py --apply       # Actually reprocess
"""

import os
import sys
import json
import glob
import time
import hashlib

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR = os.path.join(SCRIPT_DIR, "..")
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

RAW_PDF_DIR = os.path.join(BACKEND_DIR, "data", "raw_pdfs")
STRUCTURED_DIR = os.path.join(BACKEND_DIR, "data", "structured")


def file_hash(filepath: str) -> str:
    """Compute MD5 hash of a file to detect exact duplicates."""
    h = hashlib.md5()
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def find_duplicate_pdfs(pdf_dir: str) -> tuple:
    """
    Find duplicate PDFs by file hash.
    Returns (unique_pdfs, duplicate_pdfs) where each is a list of full paths.
    """
    hash_map = {}  # hash -> first file path
    unique = []
    duplicates = []

    all_pdfs = sorted(glob.glob(os.path.join(pdf_dir, "*.pdf")))

    for pdf_path in all_pdfs:
        h = file_hash(pdf_path)
        if h in hash_map:
            duplicates.append((pdf_path, hash_map[h]))  # (duplicate, original)
        else:
            hash_map[h] = pdf_path
            unique.append(pdf_path)

    return unique, duplicates


def main():
    apply = "--apply" in sys.argv

    if apply:
        print("=" * 60)
        print("  MODE: APPLY — Will DELETE old JSONs, remove duplicate")
        print("  PDFs, and reprocess all unique PDFs")
        print("=" * 60)
    else:
        print("=" * 60)
        print("  MODE: DRY RUN — Preview only (use --apply to execute)")
        print("=" * 60)

    # Find all PDFs and detect duplicates
    all_pdfs = sorted(glob.glob(os.path.join(RAW_PDF_DIR, "*.pdf")))
    unique_pdfs, duplicate_pdfs = find_duplicate_pdfs(RAW_PDF_DIR)

    # Find existing JSONs
    existing_jsons = glob.glob(os.path.join(STRUCTURED_DIR, "*.json"))

    print(f"\n  Total PDFs:      {len(all_pdfs)}")
    print(f"  Unique PDFs:     {len(unique_pdfs)}")
    print(f"  Duplicate PDFs:  {len(duplicate_pdfs)}")
    print(f"  Existing JSONs:  {len(existing_jsons)}")

    if duplicate_pdfs:
        print(f"\n  Duplicates to remove:")
        for dup, orig in duplicate_pdfs:
            print(f"    DELETE: {os.path.basename(dup)}")
            print(f"      same as: {os.path.basename(orig)}")

    if not apply:
        print(f"\n  Would DELETE {len(existing_jsons)} existing JSONs")
        print(f"  Would DELETE {len(duplicate_pdfs)} duplicate PDFs")
        print(f"  Would reprocess {len(unique_pdfs)} unique PDFs")
        print(f"\n  Run with --apply to execute.")
        return

    # Step 1: Delete existing JSONs
    print(f"\n[Step 1] Deleting {len(existing_jsons)} existing JSONs...")
    for jpath in existing_jsons:
        os.remove(jpath)
    print(f"  Done.")

    # Step 2: Remove duplicate PDFs
    print(f"\n[Step 2] Removing {len(duplicate_pdfs)} duplicate PDFs...")
    for dup_path, orig_path in duplicate_pdfs:
        os.remove(dup_path)
        print(f"  Removed: {os.path.basename(dup_path)}")
    print(f"  Done.")

    # Step 3: Import processor (requires pytesseract, PyMuPDF)
    from services.fir_processor import process_fir_pdf, generate_fir_filename

    # Step 4: Reprocess each unique PDF
    print(f"\n[Step 3] Reprocessing {len(unique_pdfs)} unique PDFs...")
    os.makedirs(STRUCTURED_DIR, exist_ok=True)

    success = 0
    errors = []
    # Track FIR numbers to detect duplicates from CONTENT (same FIR uploaded with different filenames)
    seen_fir_numbers = {}  # fir_number -> json filename

    for i, pdf_path in enumerate(unique_pdfs, 1):
        pdf_name = os.path.basename(pdf_path)
        print(f"\n  [{i}/{len(unique_pdfs)}] {pdf_name}")

        try:
            start = time.time()
            processed = process_fir_pdf(pdf_path)
            elapsed = time.time() - start

            fir_number = processed.get("fir_number")
            station = processed.get("police_station")
            district = processed.get("district")

            # Check if same FIR number already processed (content duplicate)
            if fir_number and fir_number in seen_fir_numbers:
                print(f"    SKIP — FIR {fir_number} already processed as {seen_fir_numbers[fir_number]}")
                # Remove the duplicate PDF file too
                os.remove(pdf_path)
                print(f"    Removed duplicate PDF: {pdf_name}")
                continue

            # Generate proper filename
            proper_name = generate_fir_filename(
                fir_number=fir_number,
                police_station=station,
                fallback_name=os.path.splitext(pdf_name)[0],
                extension=".json",
            )

            # Build structured JSON
            structured = {
                "file": proper_name,
                "fir_number": fir_number,
                "date": processed.get("fir_date"),
                "district": district,
                "police_station": station,
                "acts": processed.get("acts", []),
                "place": processed.get("place"),
                "complainant": processed.get("complainant", {}),
                "accused": processed.get("accused", []),
                "narrative": processed.get("narrative", ""),
                "full_text": processed.get("full_text", ""),
                "source_pdf": pdf_name,
            }

            # Handle filename collisions
            out_path = os.path.join(STRUCTURED_DIR, proper_name)
            if os.path.exists(out_path):
                base, ext = os.path.splitext(proper_name)
                counter = 2
                while os.path.exists(os.path.join(STRUCTURED_DIR, f"{base}_{counter}{ext}")):
                    counter += 1
                proper_name = f"{base}_{counter}{ext}"
                structured["file"] = proper_name
                out_path = os.path.join(STRUCTURED_DIR, proper_name)

            # Save JSON
            with open(out_path, "w", encoding="utf-8") as f:
                json.dump(structured, f, indent=2, ensure_ascii=False)

            # Track this FIR number
            if fir_number:
                seen_fir_numbers[fir_number] = proper_name

            # Rename PDF to proper name if it has a hash name
            proper_pdf_name = generate_fir_filename(
                fir_number=fir_number,
                police_station=station,
                fallback_name=pdf_name,
                extension=".pdf",
            )
            if proper_pdf_name != pdf_name:
                new_pdf_path = os.path.join(RAW_PDF_DIR, proper_pdf_name)
                if not os.path.exists(new_pdf_path):
                    os.rename(pdf_path, new_pdf_path)
                    structured["source_pdf"] = proper_pdf_name
                    # Re-save JSON with updated source_pdf
                    with open(out_path, "w", encoding="utf-8") as f:
                        json.dump(structured, f, indent=2, ensure_ascii=False)
                    print(f"    Renamed PDF: {pdf_name} -> {proper_pdf_name}")

            # Summary
            n_accused = len(processed.get("accused", []))
            n_acts = len(processed.get("acts", []))
            narr_len = len(processed.get("narrative", ""))
            print(f"    -> {proper_name}")
            print(f"       FIR: {fir_number or '???'} | {station or '???'} | "
                  f"Acts: {n_acts} | Accused: {n_accused} | "
                  f"Narr: {narr_len} chars | {elapsed:.1f}s")

            success += 1

        except Exception as e:
            print(f"    ERROR: {e}")
            errors.append(f"{pdf_name}: {e}")

    # Final summary
    print("\n" + "=" * 60)
    print(f"  Reprocessing complete!")
    print(f"  Processed:    {success}/{len(unique_pdfs)}")
    print(f"  Duplicates:   {len(duplicate_pdfs)} file duplicates removed")
    if errors:
        print(f"  Errors:       {len(errors)}")
        for e in errors:
            print(f"    - {e}")
    print(f"  Output dir:   {STRUCTURED_DIR}")
    print("=" * 60)


if __name__ == "__main__":
    main()
