import os
import fitz  # PyMuPDF
import pytesseract
from PIL import Image
import io

RAW_DIR = "data/raw_pdfs"
OUT_DIR = "data/extracted_text"

os.makedirs(OUT_DIR, exist_ok=True)

files = os.listdir(RAW_DIR)

print("Found files:", files)

for file in files:
    if file.endswith(".pdf"):
        print("Processing:", file)

        pdf_path = os.path.join(RAW_DIR, file)
        doc = fitz.open(pdf_path)

        full_text = ""

        for page_number in range(len(doc)):
            page = doc[page_number]

            # Convert page to high-resolution image
            pix = page.get_pixmap(dpi=300)
            img = Image.open(io.BytesIO(pix.tobytes("png")))

            # OCR with Malayalam + English
            text = pytesseract.image_to_string(
                img,
                lang="mal+eng",
                config="--oem 3 --psm 6"
            )

            full_text += text + "\n"

        output_path = os.path.join(OUT_DIR, file.replace(".pdf", ".txt"))

        with open(output_path, "w", encoding="utf-8") as f:
            f.write(full_text)

        print("Saved:", output_path)