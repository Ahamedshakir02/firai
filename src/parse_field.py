import re

def extract(pattern, text, default=""):
    m = re.search(pattern, text, re.IGNORECASE)
    return m.group(1).strip() if m else default

def parse_fir(text):
    return {
        "fir_no": extract(r"FIR No.*?:\s*([0-9/]+)", text),
        "district": extract(r"District.*?:\s*([A-Za-z]+)", text),
        "police_station": extract(r"PS.*?:\s*([A-Za-z]+)", text),
        "fir_datetime": extract(r"Date and Time of FIR.*?:\s*([0-9:/ ]+)", text),
        "sections": list(set(re.findall(r"\b\d+\(?\d*\)?\b", text))),
        "summary": extract(r"12\..*?\n(.*?)\n13\.", text)
    }
