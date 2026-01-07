import os
import re

INPUT_DIR = "data/extracted_text"
OUTPUT_DIR = "data/clean_text"

os.makedirs(OUTPUT_DIR, exist_ok=True)

files = os.listdir(INPUT_DIR)

print("Files to clean:", files)

for file in files:
    if file.endswith(".txt"):
        with open(os.path.join(INPUT_DIR, file), "r", encoding="utf-8") as f:
            text = f.read()

        # remove extra spaces and newlines
        text = re.sub(r'\s+', ' ', text)

        # remove page numbers like "Page 1"
        text = re.sub(r'Page\s*\d+', '', text, flags=re.IGNORECASE)

        # remove extra spaces again
        text = text.strip()

        output_path = os.path.join(OUTPUT_DIR, file)

        with open(output_path, "w", encoding="utf-8") as f:
            f.write(text)

        print("Cleaned:", file)
