import fitz
import re
import json
import os
import glob

def extract_sections(pdf_path, act_name):
    print(f"Extracting sections from {pdf_path} ({act_name})...")
    doc = fitz.open(pdf_path)
    
    full_text = ""
    for page in doc:
        full_text += page.get_text("text") + "\n"
        
    # Very basic heuristic to find sections:
    # "103. Punishment for murder.—(1) Whoever commits murder..."
    # We will look for lines starting with a number followed by a dot.
    
    lines = full_text.split('\n')
    sections = []
    current_section = None
    current_text = []
    
    section_pattern = re.compile(r'^(\d+[a-zA-Z]?)\.\s+(.*)')
    
    # Skip arrangement of sections (Table of Contents) usually in the first few pages
    # We'll just start processing after we see "CHAPTER I"
    in_content = False
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        if "CHAPTER I" in line and not in_content:
            in_content = True
            
        if not in_content:
            continue
            
        match = section_pattern.match(line)
        if match:
            # We found a new section
            if current_section:
                sections.append({
                    "act": act_name,
                    "section": current_section["num"],
                    "title": current_section["title"],
                    "description": "\n".join(current_text).strip()
                })
            
            # Reset for next section
            sec_num = match.group(1)
            title = match.group(2)
            
            # Sometimes title has a dash marking the start of description
            desc_start = ""
            if ".—" in title:
                parts = title.split(".—", 1)
                title = parts[0]
                desc_start = parts[1]
            elif "—" in title:
                parts = title.split("—", 1)
                title = parts[0]
                desc_start = parts[1]
                
            current_section = {"num": sec_num, "title": title}
            current_text = [desc_start] if desc_start else []
        else:
            if current_section:
                current_text.append(line)
                
    # Append the last one
    if current_section:
        sections.append({
            "act": act_name,
            "section": current_section["num"],
            "title": current_section["title"],
            "description": "\n".join(current_text).strip()
        })
        
    print(f"Extracted {len(sections)} sections from {act_name}")
    return sections

def main():
    rules_dir = "backend/data/rules"
    output_file = os.path.join(rules_dir, "extracted_rules.json")
    
    all_sections = []
    
    # Map filenames to Act Names
    files = {
        "repealedfileopen.pdf": "IPC",
        "a202345.pdf": "BNS",
        "a1988-59.pdf": "MVA"  # Motor Vehicles Act
    }
    
    for filename, act_name in files.items():
        pdf_path = os.path.join(rules_dir, filename)
        if os.path.exists(pdf_path):
            sections = extract_sections(pdf_path, act_name)
            all_sections.append({
                "act": act_name,
                "sections": sections
            })
        else:
            print(f"File {pdf_path} not found.")
            
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(all_sections, f, indent=2)
        
    print(f"Successfully saved {sum(len(a['sections']) for a in all_sections)} total sections to {output_file}")

if __name__ == "__main__":
    main()
