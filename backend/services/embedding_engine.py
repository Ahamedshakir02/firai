"""
Embedding Engine Service
------------------------
Generates and manages narrative embeddings for similarity search.
Refactored from existing embedding_store.py and retrieval_engine.py.
"""

import os
import json
import numpy as np
from typing import List, Optional
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from config import get_settings

settings = get_settings()


class EmbeddingEngine:
    """Manages narrative embeddings for FIR similarity search."""

    def __init__(self):
        self.model: Optional[SentenceTransformer] = None
        self.embeddings: Optional[np.ndarray] = None
        self.metadata: Optional[list] = None
        self._loaded = False

    def _ensure_model(self):
        """Load the sentence transformer model (called at startup or on first use)."""
        if self.model is None:
            print("[EmbeddingEngine] Loading model:", settings.EMBEDDING_MODEL)
            self.model = SentenceTransformer(settings.EMBEDDING_MODEL)
            print("[EmbeddingEngine] Model loaded.")

    def warmup(self):
        """Pre-load the model at startup so first user request isn't slow."""
        self._ensure_model()
        # Warm up the model with a dummy encode to JIT-compile torch ops
        self.model.encode(["warmup"], normalize_embeddings=True)
        print("[EmbeddingEngine] Warmup complete.")

    def load_store(self):
        """Load pre-computed embeddings from storage."""
        emb_path = os.path.join(settings.STORAGE_DIR, "embeddings.npy")
        meta_path = os.path.join(settings.STORAGE_DIR, "metadata.json")

        if os.path.exists(emb_path) and os.path.exists(meta_path):
            self.embeddings = np.load(emb_path)
            with open(meta_path, "r", encoding="utf-8") as f:
                self.metadata = json.load(f)
            self._loaded = True
            print(f"[EmbeddingEngine] Loaded {len(self.metadata)} embeddings from storage.")
        else:
            print("[EmbeddingEngine] No pre-computed embeddings found.")
            self.embeddings = np.array([])
            self.metadata = []
            self._loaded = True

    def encode_narrative(self, narrative: str) -> np.ndarray:
        """Encode a single narrative text into an embedding vector."""
        self._ensure_model()
        return self.model.encode([narrative], normalize_embeddings=True)[0]

    def encode_narratives(self, narratives: List[str]) -> np.ndarray:
        """Encode multiple narrative texts into embedding vectors."""
        self._ensure_model()
        return self.model.encode(narratives, normalize_embeddings=True)

    def find_similar(self, narrative: str, top_k: int = 5) -> list:
        """
        Find similar FIRs based on narrative text similarity.
        Returns list of {metadata, score} dicts.
        """
        if not self._loaded:
            self.load_store()

        if self.embeddings is None or len(self.embeddings) == 0:
            return []

        self._ensure_model()
        query_embedding = self.model.encode([narrative], normalize_embeddings=True)
        similarities = cosine_similarity(query_embedding, self.embeddings)[0]

        top_indices = np.argsort(similarities)[::-1][:top_k]

        results = []
        for idx in top_indices:
            result = {
                "score": float(similarities[idx]),
                "metadata": self.metadata[idx] if idx < len(self.metadata) else {}
            }
            results.append(result)

        return results

    def find_similar_by_vector(self, embedding_vector: np.ndarray, top_k: int = 5, exclude_idx: int = -1) -> list:
        """Find similar FIRs using a pre-computed embedding vector."""
        if not self._loaded:
            self.load_store()

        if self.embeddings is None or len(self.embeddings) == 0:
            return []

        query = embedding_vector.reshape(1, -1)
        similarities = cosine_similarity(query, self.embeddings)[0]

        top_indices = np.argsort(similarities)[::-1]

        results = []
        for idx in top_indices:
            if idx == exclude_idx:
                continue
            if len(results) >= top_k:
                break
            result = {
                "score": float(similarities[idx]),
                "metadata": self.metadata[idx] if idx < len(self.metadata) else {}
            }
            results.append(result)

        return results

    def rebuild_store(self, fir_data_list: list):
        """
        Rebuild the embedding store from a list of FIR data dicts.
        Each dict must have 'narrative' key.
        """
        narratives = []
        metadata = []

        for data in fir_data_list:
            narrative = data.get("narrative", "").strip()
            if narrative:
                narratives.append(narrative)
                metadata.append(data)

        if not narratives:
            print("[EmbeddingEngine] No narratives to encode.")
            return

        self._ensure_model()
        print(f"[EmbeddingEngine] Encoding {len(narratives)} narratives...")
        embeddings = self.model.encode(narratives, normalize_embeddings=True)

        os.makedirs(settings.STORAGE_DIR, exist_ok=True)
        np.save(os.path.join(settings.STORAGE_DIR, "embeddings.npy"), embeddings)

        with open(os.path.join(settings.STORAGE_DIR, "metadata.json"), "w", encoding="utf-8") as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)

        self.embeddings = embeddings
        self.metadata = metadata
        self._loaded = True
        print(f"[EmbeddingEngine] Store rebuilt with {len(narratives)} entries.")


# Singleton instance
embedding_engine = EmbeddingEngine()
