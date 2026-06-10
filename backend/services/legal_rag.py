"""
Legal RAG (Retrieval-Augmented Generation)
==========================================
Semantic search over 390+ parsed law sections using sentence-transformers.
No external LLM — reuses the shared sentence-transformer embedding model
(see config.EMBEDDING_MODEL) and cosine similarity for retrieval.

On startup, encodes all law sections into embeddings.
On query, finds the most semantically relevant sections.
"""

import os
import json
import numpy as np
from typing import List, Optional

# Lazy imports — loaded on warmup
_model = None
_section_embeddings = None
_sections_data = None


def warmup():
    """
    Pre-encode all law sections on startup.
    Called from main.py lifespan.
    """
    global _model, _section_embeddings, _sections_data

    print("[LegalRAG] Warming up — loading sections and encoding...")

    # Load parsed law sections
    datasets_dir = os.path.join(
        os.path.dirname(__file__), "..", "ai_engine", "data", "datasets"
    )
    sections_path = os.path.join(datasets_dir, "law_sections.json")

    # Also load legal corpus for richer data
    corpus_sections = []
    try:
        from ai_engine.data.legal_corpus import LEGAL_CORPUS
        corpus_sections = LEGAL_CORPUS
    except ImportError:
        pass

    # Load parsed PDF sections
    pdf_sections = []
    if os.path.exists(sections_path):
        with open(sections_path, "r", encoding="utf-8") as f:
            pdf_sections = json.load(f)

    # Combine both sources (deduplicate by act+section)
    seen = set()
    all_sections = []

    # Corpus first (richer data with elements, investigation steps)
    for s in corpus_sections:
        key = (s.get("act", ""), s.get("section", ""))
        if key not in seen:
            seen.add(key)
            all_sections.append(s)

    # Then PDF sections
    for s in pdf_sections:
        key = (s.get("act", ""), s.get("section", ""))
        if key not in seen:
            seen.add(key)
            all_sections.append(s)

    if not all_sections:
        print("[LegalRAG] No sections found — RAG disabled")
        return

    _sections_data = all_sections

    # Load embedding model (reuse from embedding_engine if available)
    try:
        from services.embedding_engine import embedding_engine
        if embedding_engine.model is not None:
            _model = embedding_engine.model
            print("[LegalRAG] Reusing embedding model from EmbeddingEngine")
        else:
            raise ValueError("EmbeddingEngine model not loaded yet")
    except Exception:
        from sentence_transformers import SentenceTransformer
        from config import get_settings
        _model = SentenceTransformer(get_settings().EMBEDDING_MODEL)
        print("[LegalRAG] Loaded fresh embedding model")

    # Encode all sections
    texts = []
    for s in all_sections:
        # Build rich text for embedding: title + description + elements
        parts = []
        if s.get("title"):
            parts.append(s["title"])
        if s.get("description"):
            parts.append(s["description"][:500])  # Cap length
        if s.get("elements"):
            parts.append("Elements: " + ", ".join(s["elements"]))
        texts.append(" ".join(parts))

    _section_embeddings = _model.encode(texts, normalize_embeddings=True, show_progress_bar=False)

    print(f"[LegalRAG] Encoded {len(all_sections)} sections ({_section_embeddings.shape})")


def search(query: str, top_k: int = 5) -> list:
    """
    Semantic search over law sections.

    Args:
        query: Natural language legal question
        top_k: Number of results to return

    Returns:
        List of {section, act, title, description, score, ...}
    """
    if _model is None or _section_embeddings is None or _sections_data is None:
        return []

    # Encode query
    query_embedding = _model.encode([query], normalize_embeddings=True)

    # Cosine similarity (embeddings are already normalized)
    similarities = np.dot(_section_embeddings, query_embedding.T).flatten()

    # Get top-k indices
    top_indices = np.argsort(similarities)[::-1][:top_k]

    results = []
    for idx in top_indices:
        score = float(similarities[idx])
        if score < 0.15:  # Skip very low relevance
            continue
        section = _sections_data[idx].copy()
        section["relevance_score"] = round(score, 4)
        results.append(section)

    return results


def is_ready() -> bool:
    """Check if RAG is initialized."""
    return _model is not None and _section_embeddings is not None
