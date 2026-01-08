import os
import re
import json

INPUT_DIR = "data/clean_text"
OUTPUT_DIR = "data/structured"

os.makedirs(OUTPUT_DIR, exist_ok=True)

files = os.listdir(INPUT_DIR)

for file in files:
    if not file.endswith(".txt"):
        continue

    with open(os.path.join(INPUT_DIR, file), "r", encoding="utf-8") as f:
        text = f.read()

    # ---------------- DATE ----------------
    date_match = re.search(r'\b\d{2}[/-]\d{2}[/-]\d{4}\b', text)
    date = date_match.group(0) if date_match else None

    # ---------------- IPC SECTIONS (LINE-STRICT) ----------------
    ipc_sections = []

    for line in text.split("\n"):
        l = line.upper()
        if "U/S" in l and "IPC" in l:
            match = re.search(r'U/S\s*(.*?)\s*,?\s*IPC', line, re.IGNORECASE)
            if match:
                raw_ipc = match.group(1)
                ipc_sections = re.findall(
                    r'\b\d{3}\([a-zA-Z]+\)|\b\d{3}\b',
                    raw_ipc
                )
            break

    ipc_sections = list(dict.fromkeys(ipc_sections))

    # ---------------- PLACE OF OCCURRENCE ----------------
    place = None

    match = re.search(
        r'Location\s*/\s*Address.*?([A-Za-z][A-Za-z\s]{3,60})',
        text,
        flags=re.IGNORECASE
    )

    if match:
        place = re.sub(r'\s+', ' ', match.group(1)).strip()

    # ---------------- COMPLAINANT NAME ----------------
    complainant = None

    match = re.search(
        r'\(a\)\.?\s*Name.*?([A-Z]{3,}(?:\s+[A-Z]{2,})?)',
        text,
        flags=re.IGNORECASE | re.DOTALL
    )

    if match:
        complainant = match.group(1).strip().upper()

    # ---------------- ACCUSED (LEVEL 5 – SECTION-AWARE GLOBAL SCAN) ----------------
    accused = []

    # Step 1: isolate accused section
    section_match = re.search(
        r'Details of known.*?accused with full particulars(.*?)(Reason for delay|Particulars of properties|$)',
        text,
        flags=re.IGNORECASE | re.DOTALL
    )

    accused_text = section_match.group(1) if section_match else ""
    # Step 2: extract NAME + AGE
    pattern = re.compile(
        r'(?:^|\n|\s)\d*\s*([A-Z][A-Z\s\.]{2,50})\s+Age[-\s]*([0-9]{1,3})',
        re.IGNORECASE
    )


    matches = pattern.findall(accused_text)
    for name, age in matches:
        name_clean = re.sub(r'\s+', ' ', name).strip().upper()

        accused.append({
            "name": name_clean,
            "age": age
        })

    # Step 3: remove duplicates
    unique = []
    seen = set()
    for a in accused:
        key = (a["name"], a["age"])
        if key not in seen:
            seen.add(key)
            unique.append(a)

    accused = unique
    # ---------------- OUTPUT ----------------
    data = {
        "file": file,
        "date": date,
        "ipc_sections": ipc_sections,
        "place": place,
        "complainant": complainant,
        "accused": accused,
        "full_text": text
    }

    output_file = file.replace(".txt", ".json")
    with open(os.path.join(OUTPUT_DIR, output_file), "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print("Structured:", output_file)
