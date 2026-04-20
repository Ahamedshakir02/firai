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
import re as _re
from config import get_settings

settings = get_settings()

# ── Boilerplate phrases commonly found in Kerala Police FIR narratives ──
# These are template/format phrases that appear in every FIR regardless of crime type.
# Stripping them before encoding ensures embeddings capture only the actual incident.
_BOILERPLATE_PATTERNS = [
    # English FIR template phrases
    r'Before the Hon\'ble.*?(?:BNSS|BNS|IPC).*?പ്രകാരം\)',
    r'District\s*\(ജില്ല\)\s*:.*?(?=\d{2}[/\-]\d{2}[/\-]\d{4}|$)',
    r'FIR\s*No[^:]*:.*?\d{4}',
    r'Date and Time of FIR.*?\d{2}:\d{2}',
    r'SI\s*No\.\s*Acts\s*Sections.*?(?=\d{2}[/\-]\d{2})',
    r'Occurrence of Offence.*?(?=First Information Contents|എഫ്\u200c\.ഐ\.ആര്\u200d)',
    r'Information Received at P\.S.*?hrs',
    r'General Diary References.*?hrs',
    r'Type of Information.*?(?:Oral|Written|Suo Mottu)',
    r'Source of Complainant.*?(?:Citizen|General Public|Suo Mottu)',
    r'Place of Occurrence.*?(?=Complainant|പരാതിക്കാരന്)',
    r'Direction and distance from P\.S.*',
    r'Beat No.*',
    r'Complainant / Informant.*',
    r'Father\'s / Mother\'s / Husband\'s Name.*',
    r'Nationality.*?INDIA',
    r'UID No\..*',
    r'Passport No\..*',
    r'ID details.*?(?:PAN|പാന്\u200d)',
    r'Occupation\s*\(.*?\)\s*:',
    r'Address Type\s*Address.*',
    r'Permanent Address.*?INDIA',
    r'Present Address.*?INDIA',
    r'Land Phone Number.*',
    r'Mobile Number.*?\d+',
    r'Victim / Missing / Deceased details.*',
    r'Details of known.*?accused with full particulars.*',
    r'Reason for delay in reporting.*',
    r'Particulars of properties of interest.*',
    r'Total value of property stolen.*',
    r'Inquest Report.*',
    r'Action taken:.*?(?=Submitted|$)',
    r'Directed to take up the Investigation.*',
    r'Performing Self Investigation.*',
    r'Name of.*?Investigation.*',
    r'F\.I\.R\.read over to the complainant.*',
    r'R\.O\.A\.C.*',
    r'Signature / Thumb impression.*',
    r'Date and time of dispatch to the court.*',
    r'computer generated document.*',
    r'Scan the QR Code.*',
    r'https://thuna\.keralapolice\.gov\.in.*',
    r'Helpline Number of District Legal Services Authority.*',
    # Common Malayalam template phrases (present in every FIR)
    r'സ്റ്റേഷനില്\u200d ഹാജരായി',  # appeared at the station
    r'മൊഴി രേഖപ്പെടുത്തി',  # recorded the statement
    r'ഹാജരാക്കിത്തന്നത്\u200c',
    r'ഹാജരാക്കി തന്നത്\u200c',
    r'കേസ്\u200c?\s*രജിസ്റ്റര്\u200d\s*ചെയ്യുന്നു',  # registering the case
    r'അസ്സല്\u200d മൊഴി ഇതൊന്നിച്ചുണ്ട്\u200c',
    r'സബ്\u200c?\s*ഇന്\u200dസ്പെക്ടര്\u200d\s*ഓഫ്\u200c?\s*പോലീസ്\u200c',
    r'ഇന്\u200dസ്പെക്ടര്\u200d\s*ഓഫ്\u200c?\s*പോലീസ്\u200c',
    r'പോലീസ്\u200c?\s*സ്റ്റേഷന്\u200d',
    r'U/[Ss]\s*\d+.*?(?:IPC|BNS|MV Act|Abkari Act)',
    r'ക്രൈം[\.\s]*\d+/\d+',
    r'Submitted\s*Name.*',
    r'Rank\s*\(.*?\)\s*:.*',
    r'PEN\s*\(.*?\)\s*:.*',
    r'PS\s*\(.*?\)\s*:.*',
    r'\d+/\d+\s*$',  # page numbers like 3/5
]

# Compile patterns for performance
_BOILERPLATE_RE = [_re.compile(p, _re.IGNORECASE | _re.DOTALL) for p in _BOILERPLATE_PATTERNS]


def strip_fir_boilerplate(text: str) -> str:
    """
    Remove common FIR template/format text from a narrative.
    Returns only the meaningful incident description.
    """
    if not text:
        return text

    cleaned = text
    for pattern in _BOILERPLATE_RE:
        cleaned = pattern.sub(' ', cleaned)

    # Collapse whitespace
    cleaned = _re.sub(r'\s+', ' ', cleaned).strip()

    # If we stripped too aggressively and have very little left, return original
    if len(cleaned) < 30 and len(text) > 50:
        return text

    return cleaned


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
        """Encode a single narrative text into an embedding vector.
        Strips FIR boilerplate before encoding so embeddings capture only incident content."""
        self._ensure_model()
        cleaned = strip_fir_boilerplate(narrative)
        return self.model.encode([cleaned], normalize_embeddings=True)[0]

    def encode_narratives(self, narratives: List[str]) -> np.ndarray:
        """Encode multiple narrative texts into embedding vectors.
        Strips FIR boilerplate before encoding."""
        self._ensure_model()
        cleaned = [strip_fir_boilerplate(n) for n in narratives]
        return self.model.encode(cleaned, normalize_embeddings=True)

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
