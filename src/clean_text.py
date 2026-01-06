import re
from pathlib import Path

TEXT_DIR = Path("../data/text")

def clean(text):
    text = re.sub(r"https?://\S+", "", text)
    text = re.sub(r"This is a computer generated document.*", "", text)
    text = re.sub(r"\n{2,}", "\n", text)
    text = re.sub(r"[ \t]{2,}", " ", text)
    return text.strip()

if __name__ == "__main__":
    for txt in TEXT_DIR.glob("*.txt"):
        cleaned = clean(txt.read_text(encoding="utf-8"))
        txt.write_text(cleaned, encoding="utf-8")
        print("Cleaned:", txt.name)
