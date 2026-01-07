import os
from PyPDF2 import PdfReader

RAW_DIR = "data/raw_pdfs"
OUT_DIR = "data/extracted_text"

os.makedirs(OUT_DIR, exist_ok=True)

files = os.listdir(RAW_DIR)

print("Found files:", files)

for file in files:
    if file.endswith(".pdf"):
        print("Reading:", file)

        reader = PdfReader(os.path.join(RAW_DIR, file))
        text = ""

        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"

        output_path = os.path.join(OUT_DIR, file.replace(".pdf", ".txt"))
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(text)

        print("Saved:", output_path)
