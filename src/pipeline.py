from pathlib import Path
from parse_fields import parse_fir
import json

TEXT_DIR = Path("../data/text")
OUT_DIR = Path("../data/processed")
OUT_DIR.mkdir(exist_ok=True)

if __name__ == "__main__":
    for txt in TEXT_DIR.glob("*.txt"):
        data = parse_fir(txt.read_text(encoding="utf-8"))
        out = OUT_DIR / f"{txt.stem}.json"
        out.write_text(json.dumps(data, indent=4, ensure_ascii=False))
        print("Processed:", out.name)
