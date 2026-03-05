import os
import fitz  # PyMuPDF
import pytesseract
from PIL import Image
import io


def extract_text_from_pdf(pdf_path):
    """
    Extract text from a single FIR PDF using OCR.
    Used by the API when a new FIR is uploaded.
    """

    doc = fitz.open(pdf_path)
    full_text = ""

    for page_number in range(len(doc)):
        page = doc[page_number]

        pix = page.get_pixmap(dpi=300)
        img = Image.open(io.BytesIO(pix.tobytes("png")))

        text = pytesseract.image_to_string(
            img,
            lang="mal+eng",
            config="--oem 3 --psm 6"
        )

        full_text += text + "\n"

    return full_text


def batch_extract(raw_dir="data/raw_pdfs", out_dir="data/extracted_text"):
    """
    Optional batch pipeline used only for preprocessing datasets.
    """

    os.makedirs(out_dir, exist_ok=True)

    files = os.listdir(raw_dir)
    print("Found files:", files)

    for file in files:
        if file.endswith(".pdf"):
            print("Processing:", file)

            pdf_path = os.path.join(raw_dir, file)

            text = extract_text_from_pdf(pdf_path)

            output_path = os.path.join(out_dir, file.replace(".pdf", ".txt"))

            with open(output_path, "w", encoding="utf-8") as f:
                f.write(text)

            print("Saved:", output_path)


if __name__ == "__main__":
    batch_extract()