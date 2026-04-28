"""
FirClassifier — Custom BiLSTM Neural Network for Crime Classification
=====================================================================
Architecture: Embedding → BiLSTM → Attention → Dense → Softmax
Designed from scratch for Kerala Police FIR narratives.
Handles Malayalam and English text.
"""

import torch
import torch.nn as nn
import numpy as np
import json
import os
import re
import pickle
from typing import Optional, Tuple
from collections import Counter


# ══════════════════ VOCABULARY BUILDER ══════════════════

class FirVocabulary:
    """Custom vocabulary for FIR narratives (Malayalam + English)."""

    PAD_TOKEN = "<PAD>"
    UNK_TOKEN = "<UNK>"

    def __init__(self, max_vocab_size: int = 10000):
        self.word2idx = {self.PAD_TOKEN: 0, self.UNK_TOKEN: 1}
        self.idx2word = {0: self.PAD_TOKEN, 1: self.UNK_TOKEN}
        self.word_counts = Counter()
        self.max_vocab_size = max_vocab_size

    def tokenize(self, text: str) -> list:
        """Simple whitespace + punctuation tokenizer for Malayalam/English."""
        text = text.lower().strip()
        # Split on whitespace and punctuation, keep Malayalam characters
        tokens = re.findall(r'[\w\u0D00-\u0D7F]+', text)
        return tokens

    def build_vocab(self, texts: list):
        """Build vocabulary from a list of texts."""
        for text in texts:
            tokens = self.tokenize(text)
            self.word_counts.update(tokens)

        # Keep top N most frequent words
        most_common = self.word_counts.most_common(self.max_vocab_size - 2)
        for idx, (word, _) in enumerate(most_common, start=2):
            self.word2idx[word] = idx
            self.idx2word[idx] = word

        print(f"[Vocabulary] Built vocab with {len(self.word2idx)} tokens")

    def encode(self, text: str, max_len: int = 256) -> list:
        """Convert text to list of token indices."""
        tokens = self.tokenize(text)[:max_len]
        indices = [self.word2idx.get(t, 1) for t in tokens]  # 1 = UNK
        # Pad to max_len
        indices += [0] * (max_len - len(indices))
        return indices

    def save(self, path: str):
        with open(path, "wb") as f:
            pickle.dump({"word2idx": self.word2idx, "idx2word": self.idx2word}, f)

    def load(self, path: str):
        with open(path, "rb") as f:
            data = pickle.load(f)
        self.word2idx = data["word2idx"]
        self.idx2word = data["idx2word"]


# ══════════════════ LABEL ENCODER ══════════════════

class CrimeLabels:
    """Encode crime types and severity as integer labels."""

    CRIME_TYPES = [
        "assault", "theft", "robbery", "cheating", "trespass",
        "murder", "homicide", "kidnapping", "sexual_offense",
        "cyber_crime", "drug_offense", "drunk_driving", "rash_driving",
        "road_accident", "forgery", "excise_offense",
        "criminal_intimidation", "unnatural_death", "illegal_mining",
        "missing_person", "domestic_violence", "property_damage",
        "fraud", "public_nuisance", "wrongful_restraint",
        "wrongful_confinement", "breach_of_trust", "stolen_property",
        "abetment_of_suicide", "death_by_negligence", "dacoity",
        "extortion", "house_breaking", "counterfeit", "arms_offense",
        "atrocity", "public_servant_offense", "other"
    ]

    SEVERITY_LEVELS = ["low", "medium", "high", "critical"]

    def __init__(self):
        self.crime2idx = {c: i for i, c in enumerate(self.CRIME_TYPES)}
        self.idx2crime = {i: c for c, i in self.crime2idx.items()}
        self.sev2idx = {s: i for i, s in enumerate(self.SEVERITY_LEVELS)}
        self.idx2sev = {i: s for s, i in self.sev2idx.items()}

    @property
    def num_crimes(self):
        return len(self.CRIME_TYPES)

    @property
    def num_severities(self):
        return len(self.SEVERITY_LEVELS)

    def encode_crime(self, crime_type: str) -> int:
        return self.crime2idx.get(crime_type, self.crime2idx["other"])

    def decode_crime(self, idx: int) -> str:
        return self.idx2crime.get(idx, "other")

    def encode_severity(self, severity: str) -> int:
        return self.sev2idx.get(severity, self.sev2idx["medium"])

    def decode_severity(self, idx: int) -> str:
        return self.idx2sev.get(idx, "medium")


# ══════════════════ ATTENTION LAYER ══════════════════

class Attention(nn.Module):
    """Self-attention mechanism to focus on important parts of the narrative."""

    def __init__(self, hidden_size: int):
        super().__init__()
        self.attention = nn.Linear(hidden_size, 1)

    def forward(self, lstm_output: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor]:
        # lstm_output: (batch, seq_len, hidden_size)
        weights = torch.softmax(self.attention(lstm_output), dim=1)
        # Weighted sum
        context = torch.sum(weights * lstm_output, dim=1)
        return context, weights.squeeze(-1)


# ══════════════════ BiLSTM CLASSIFIER MODEL ══════════════════

class FirClassifierModel(nn.Module):
    """
    Custom BiLSTM neural network for crime classification.

    Architecture:
        Input text → Embedding(vocab_size, embed_dim)
        → BiLSTM(embed_dim, hidden_size, num_layers)
        → Self-Attention
        → Dense(hidden*2, 128) → ReLU → Dropout
        → Crime head: Dense(128, num_crimes)
        → Severity head: Dense(128, num_severities)
    """

    def __init__(
        self,
        vocab_size: int = 10000,
        embed_dim: int = 128,
        hidden_size: int = 128,
        num_layers: int = 2,
        num_crimes: int = 38,
        num_severities: int = 4,
        dropout: float = 0.3
    ):
        super().__init__()

        self.embedding = nn.Embedding(vocab_size, embed_dim, padding_idx=0)
        self.lstm = nn.LSTM(
            embed_dim, hidden_size,
            num_layers=num_layers,
            bidirectional=True,
            batch_first=True,
            dropout=dropout if num_layers > 1 else 0
        )
        self.attention = Attention(hidden_size * 2)  # *2 for bidirectional
        self.fc = nn.Sequential(
            nn.Linear(hidden_size * 2, 128),
            nn.ReLU(),
            nn.Dropout(dropout),
        )
        # Multi-task heads
        self.crime_head = nn.Linear(128, num_crimes)
        self.severity_head = nn.Linear(128, num_severities)

    def forward(self, x: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
        """
        Args:
            x: (batch, seq_len) token indices
        Returns:
            crime_logits, severity_logits, attention_weights
        """
        embedded = self.embedding(x)  # (batch, seq_len, embed_dim)
        lstm_out, _ = self.lstm(embedded)  # (batch, seq_len, hidden*2)
        context, attn_weights = self.attention(lstm_out)  # (batch, hidden*2)
        features = self.fc(context)  # (batch, 128)

        crime_logits = self.crime_head(features)  # (batch, num_crimes)
        severity_logits = self.severity_head(features)  # (batch, num_severities)

        return crime_logits, severity_logits, attn_weights


# ══════════════════ HIGH-LEVEL CLASSIFIER ══════════════════

class FirClassifier:
    """
    High-level crime classifier that wraps the neural network.
    Handles vocabulary, label encoding, model loading, and prediction.
    """

    def __init__(self, model_dir: str = None):
        self.vocab = FirVocabulary()
        self.labels = CrimeLabels()
        self.model: Optional[FirClassifierModel] = None
        self.device = torch.device("cpu")
        self.model_dir = model_dir or os.path.join(
            os.path.dirname(__file__), "..", "trained_models"
        )
        self._loaded = False

    def load(self) -> bool:
        """Load trained model and vocabulary."""
        vocab_path = os.path.join(self.model_dir, "classifier_vocab.pkl")
        model_path = os.path.join(self.model_dir, "classifier.pt")

        if not os.path.exists(model_path) or not os.path.exists(vocab_path):
            print("[FirClassifier] No trained model found. Using fallback.")
            return False

        self.vocab.load(vocab_path)
        checkpoint = torch.load(model_path, map_location=self.device, weights_only=True)
        self.model = FirClassifierModel(
            vocab_size=len(self.vocab.word2idx),
            num_crimes=self.labels.num_crimes,
            num_severities=self.labels.num_severities,
            **checkpoint.get("model_config", {})
        )
        self.model.load_state_dict(checkpoint["model_state_dict"])
        self.model.eval()
        self._loaded = True
        print("[FirClassifier] Model loaded successfully.")
        return True

    def predict(self, narrative: str) -> dict:
        """
        Predict crime type and severity from a narrative.
        Falls back to keyword-based classification if model not loaded.
        """
        if not self._loaded or self.model is None:
            return self._fallback_predict(narrative)

        # Tokenize and encode
        indices = self.vocab.encode(narrative)
        x = torch.tensor([indices], dtype=torch.long, device=self.device)

        with torch.no_grad():
            crime_logits, sev_logits, attn_weights = self.model(x)

        crime_probs = torch.softmax(crime_logits, dim=1)[0]
        sev_probs = torch.softmax(sev_logits, dim=1)[0]

        crime_idx = torch.argmax(crime_probs).item()
        sev_idx = torch.argmax(sev_probs).item()

        # Get top-3 predictions with confidence
        top3_crimes = torch.topk(crime_probs, 3)
        predictions = []
        for prob, idx in zip(top3_crimes.values, top3_crimes.indices):
            predictions.append({
                "crime_type": self.labels.decode_crime(idx.item()),
                "confidence": round(prob.item(), 4)
            })

        return {
            "crime_type": self.labels.decode_crime(crime_idx),
            "crime_confidence": round(crime_probs[crime_idx].item(), 4),
            "severity": self.labels.decode_severity(sev_idx),
            "severity_confidence": round(sev_probs[sev_idx].item(), 4),
            "top_predictions": predictions,
        }

    def _fallback_predict(self, narrative: str) -> dict:
        """Keyword-based fallback when model isn't trained yet."""
        from ai_engine.data.label_generator import IPC_MAP, BNS_MAP
        text = narrative.lower()

        # Malayalam + English keyword matching
        KEYWORDS = {
            "murder": ["murder", "kill", "കൊല", "death", "മരണം"],
            "drunk_driving": ["മദ്യപിച്ച", "drunk", "ആല്‍ക്കോ", "breath analy", "alcohol", "മദ്യത്തിന്റെ"],
            "rash_driving": ["അതിവേഗത", "അശ്രദ്ധമായ", "rash driv", "negligent", "അവിവേകമായ"],
            "assault": ["അടിച്ച", "attack", "beat", "hit", "ചവിട്ട", "ദേഹോപദ്രവം"],
            "theft": ["മോഷ്ടി", "steal", "stolen", "കളവ്", "theft", "കള്ളന്‍"],
            "cheating": ["cheat", "fraud", "ചതി", "വഞ്ചന", "420"],
            "sexual_offense": ["modesty", "outrage", "354", "376", "ലൈംഗിക"],
            "excise_offense": ["abkari", "excise", "മദ്യം", "liquor", "പരസ്യമായി മദ്യപിക്ക"],
            "unnatural_death": ["drown", "മുങ്ങി", "unnatural death", "മരണപ്പെട്ട", "suicide"],
            "forgery": ["forge", "counterfeit", "വ്യാജ", "falsif"],
            "criminal_intimidation": ["threaten", "ഭീഷണി", "കൊല്ലും"],
            "trespass": ["trespass", "അതിക്രമിച്ച", "house breaking"],
            "property_damage": ["damage", "mischief", "നഷ്ടം വരുത്ത"],
        }

        for crime, keywords in KEYWORDS.items():
            if any(kw in text for kw in keywords):
                severity = "high"
                if crime in ("murder", "sexual_offense", "unnatural_death"):
                    severity = "critical"
                elif crime in ("excise_offense", "theft", "cheating", "forgery"):
                    severity = "medium"
                elif crime in ("public_nuisance", "wrongful_restraint"):
                    severity = "low"
                return {
                    "crime_type": crime,
                    "crime_confidence": 0.6,
                    "severity": severity,
                    "severity_confidence": 0.5,
                    "top_predictions": [{"crime_type": crime, "confidence": 0.6}],
                }

        return {
            "crime_type": "other",
            "crime_confidence": 0.3,
            "severity": "medium",
            "severity_confidence": 0.3,
            "top_predictions": [{"crime_type": "other", "confidence": 0.3}],
        }
