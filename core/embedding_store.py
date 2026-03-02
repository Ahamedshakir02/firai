import os
import json
import numpy as np
from sentence_transformers import SentenceTransformer

STRUCTURED_DIR = "data/structured"
STORAGE_DIR = "storage"
MODEL_NAME = "all-MiniLM-L6-v2"


def build_embedding_store():
    model = SentenceTransformer(MODEL_NAME)

    texts = []
    metadata = []

    for file in os.listdir(STRUCTURED_DIR):
        if not file.endswith(".json"):
            continue

        path = os.path.join(STRUCTURED_DIR, file)

        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        narrative = data.get("narrative", "").strip()
        if not narrative:
            continue

        texts.append(narrative)
        metadata.append(data)

    print("Encoding FIR narratives...")
    embeddings = model.encode(texts, normalize_embeddings=True)

    os.makedirs(STORAGE_DIR, exist_ok=True)

    np.save(os.path.join(STORAGE_DIR, "embeddings.npy"), embeddings)

    with open(os.path.join(STORAGE_DIR, "metadata.json"), "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)

    print("Embedding store built successfully.")