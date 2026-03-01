import os
import json
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

STRUCTURED_DIR = "data/structured"

# Load model
model = SentenceTransformer("all-MiniLM-L6-v2")

files = []
texts = []

# Load narratives
for file in os.listdir(STRUCTURED_DIR):
    if not file.endswith(".json"):
        continue

    path = os.path.join(STRUCTURED_DIR, file)

    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    text = data.get("narrative", "").strip()

    if text:
        files.append(file)
        texts.append(text)

print("Encoding FIR narratives...")
embeddings = model.encode(texts, normalize_embeddings=True)
print("Done.\n")

# ---- USER INPUT ----
query_file = input("Enter FIR filename (example: 1.json): ").strip()

if query_file not in files:
    print("FIR not found.")
    exit()

query_index = files.index(query_file)
query_vector = embeddings[query_index].reshape(1, -1)

similarities = cosine_similarity(query_vector, embeddings)[0]

sorted_indices = np.argsort(similarities)[::-1]

print(f"\nTop similar FIRs to {query_file}:\n")

for idx in sorted_indices:
    if files[idx] == query_file:
        continue
    print(files[idx], "Score:", round(similarities[idx], 4))