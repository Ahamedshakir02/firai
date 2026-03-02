import os
import json
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

STORAGE_DIR = "storage"
MODEL_NAME = "all-MiniLM-L6-v2"

# Load model once
model = SentenceTransformer(MODEL_NAME)

# Load embeddings
embeddings = np.load(os.path.join(STORAGE_DIR, "embeddings.npy"))

with open(os.path.join(STORAGE_DIR, "metadata.json"), "r", encoding="utf-8") as f:
    metadata = json.load(f)


def find_similar_firs(new_text, top_k=5):
    query_embedding = model.encode([new_text], normalize_embeddings=True)

    similarities = cosine_similarity(query_embedding, embeddings)[0]

    top_indices = np.argsort(similarities)[::-1][:top_k]

    results = []

    for idx in top_indices:
        result = {
            "score": float(similarities[idx]),
            "file": metadata[idx].get("file"),
            "date": metadata[idx].get("date"),
            "acts": metadata[idx].get("acts"),
        }
        results.append(result)

    return results