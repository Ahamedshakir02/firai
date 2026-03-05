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

    # ---------------- ACTS & SECTIONS (LEVEL 6 – TABLE + INLINE) ----------------
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

                    raw_sections = re.findall(
                        r'\b\d+(?:\([a-zA-Z]+\))?',
                        section_part
                    )

                    sections = []
                    for s in raw_sections:
                        num = int(re.match(r'\d+', s).group())
                        if num < 1000:  # 🔴 FILTER YEARS HERE
                            sections.append(s)

                    if sections:
                        acts.append({
                            "act": act_name,
                            "sections": list(dict.fromkeys(sections))
                        })
                j += 1
            break

    # -------- FALLBACK INLINE EXTRACTION --------
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
                acts.append({
                    "act": act_name.strip(),
                    "sections": list(dict.fromkeys(sections))
                })

    # ---------------- ACT NORMALIZATION ----------------
    normalized = []
    for a in acts:
        act_name = a["act"].upper()

        if "MOTOR" in act_name:
            act_std = "Motor Vehicle Act 1988"
        elif "BNS" in act_name or "BHARATIYA NYAYA SANHITA" in act_name:
            act_std = "Bharatiya Nyaya Sanhita (BNS)"
        elif "IPC" in act_name:
            act_std = "Indian Penal Code (IPC)"
        else:
            act_std = a["act"]

        normalized.append({
            "act": act_std,
            "sections": a["sections"]
        })

    acts = normalized

    # ---------------- ACT DOMINANCE RULE (CRITICAL FIX) ----------------
    mv_act = None
    for a in acts:
        if "Motor Vehicle Act" in a["act"]:
            mv_act = a
            break

    if mv_act:
        acts = [mv_act]   # 🚗 KEEP ONLY MV ACT

    # ---------------- PLACE ----------------
    place = None
    match = re.search(
        r'Location\s*/\s*Address.*?([A-Za-z][A-Za-z\s]{3,60})',
        text,
        flags=re.IGNORECASE
    )
    if match:
        place = re.sub(r'\s+', ' ', match.group(1)).strip()

    # ---------------- COMPLAINANT ----------------
    complainant = {
        "name": None,
        "father_name": None,
        "dob": None
    }

    name_match = re.search(
        r'\(a\)\.?\s*Name.*?([A-Z]{3,}(?:\s+[A-Z]{2,})?)',
        text,
        flags=re.IGNORECASE | re.DOTALL
    )

    father_match = re.search(
        r"Father's\s*/?\s*Mother's\s*/?\s*Husband's\s*Name.*?([A-Z\s]{3,40})",
        text,
        flags=re.IGNORECASE | re.DOTALL
    )

    dob_match = re.search(
        r'([0-9]{1,2}[/-][0-9]{1,2}[/-][0-9]{2,4})',
        text
    )

    if name_match:
        complainant["name"] = name_match.group(1).strip().upper()

    if father_match:
        father_candidate = father_match.group(1).strip().upper()

        invalid_words = [
            "DISTRICT", "KERALA", "INDIA", "MALAPPURAM",
            "ADDRESS", "PRESENT", "PERMANENT"
        ]

        if any(word in father_candidate for word in invalid_words):
            father_candidate = None

        complainant["father_name"] = father_candidate

    if dob_match:
        complainant["dob"] = dob_match.group(1)
    # ---------------- ACCUSED ----------------
    accused = []

    section_match = re.search(
        r'Details of known.*?accused with full particulars(.*?)(Reason for delay|Particulars of properties|$)',
        text,
        flags=re.IGNORECASE | re.DOTALL
    )

    accused_text = section_match.group(1) if section_match else ""

    pattern = re.compile(
        r'([A-Z][A-Z\s\.]{2,50})\s+Age[-\s]*([0-9]{1,3})',
        re.IGNORECASE
    )

    seen = set()

    for match in pattern.finditer(accused_text):

        name = match.group(1).strip().upper()

        father = None
        dob = None
        address = None

        context = accused_text[max(0, match.start()-200): match.end()+200]

        father_match = re.search(
            r'(?:FATHER|S/O|D/O|W/O)\s*[:\-]?\s*([A-Z\s]{3,40})',
            context,
            re.IGNORECASE
        )

        if father_match:
            father_candidate = father_match.group(1).strip().upper()

            invalid_words = [
                "DISTRICT", "KERALA", "INDIA",
                "ADDRESS", "PRESENT", "PERMANENT"
            ]

            if not any(w in father_candidate for w in invalid_words):
                father = father_candidate

        dob_match = re.search(
            r'([0-9]{1,2}[/-][0-9]{1,2}[/-][0-9]{2,4})',
            context
        )

        if dob_match:
            dob = dob_match.group(1)

        address_match = re.search(
            r'(?:PERMANENT|PRESENT)\s*:\s*([A-Z0-9\s,]{10,120})',
            context,
            re.IGNORECASE
        )

        if address_match:
            address = address_match.group(1).strip()

        key = name

        if key not in seen:
            seen.add(key)

            accused.append({
                "name": name,
                "father_name": father,
                "dob": dob,
                "address": address
            })
    # ---------------- NARRATIVE EXTRACTION (KEYWORD-BASED) ----------------
    narrative = None

    match = re.search(
        r'First Information Contents.*?\n(.*?)\n\s*13\.',
        text,
        flags=re.IGNORECASE | re.DOTALL
    )

    if not match:
        # fallback using Malayalam pattern
        match = re.search(
            r'First Information Contents.*?(.*?)Directed to take up the Investigation',
            text,
            flags=re.IGNORECASE | re.DOTALL
        )

    if match:
        narrative = match.group(1).strip()
        narrative = re.sub(r'\s+', ' ', narrative)
    # ---------------- NARRATIVE CLEANING ----------------

    if narrative:
        # Remove Malayalam FIR header inside brackets
        narrative = re.sub(
            r'\(.*?ഉള്ളടക്കം.*?\)',
            '',
            narrative,
            flags=re.IGNORECASE
        )

        # Remove "Action taken" section if it accidentally leaks in
        narrative = re.sub(
            r'13\..*',
            '',
            narrative,
            flags=re.IGNORECASE | re.DOTALL
        )

        # Normalize whitespace
        narrative = re.sub(r'\s+', ' ', narrative).strip()

    # ---------------- OUTPUT ----------------
    data = {
        "file": file,
        "date": date,
        "acts": acts,
        "place": place,
        "complainant": complainant,
        "accused": accused,
        "narrative": narrative,
        "full_text": text
    }

    output_file = file.replace(".txt", ".json")
    with open(os.path.join(OUTPUT_DIR, output_file), "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print("Structured:", output_file)

