import pdfplumber
from pathlib import Path

RAW_DIR = Path("../data/raw_firs")
TEXT_DIR = Path("../data/text")
TEXT_DIR.mkdir(exist_ok=True)

def extract_text(pdf_path):
    text = ""
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            if page.extract_text():
                text += page.extract_text() + "\n"
    return text

if __name__ == "__main__":
    for pdf in RAW_DIR.glob("*.pdf"):
        text = extract_text(pdf)
        out = TEXT_DIR / f"{pdf.stem}.txt"
        out.write_text(text, encoding="utf-8")
        print("Extracted:", pdf.name)
