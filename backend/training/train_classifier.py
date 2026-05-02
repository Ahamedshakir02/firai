"""
FirAI — Custom Crime Classifier Training Script
=================================================
Run this on Google Colab (free T4 GPU) or locally.

Usage on Colab:
  1. Upload this file + ai_engine/ folder + data/structured/ folder
  2. Run: !python train_classifier.py --data_dir ./data/structured --epochs 50
  3. Download the trained model from ./trained_models/

Usage locally:
  python training/train_classifier.py --data_dir backend/data/structured --epochs 50
"""

import os
import sys
import json
import argparse
import random
import re
import pickle
import numpy as np
from collections import Counter

# ── Ensure ai_engine is importable ──
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR = os.path.join(SCRIPT_DIR, "..")
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader

from ai_engine.data.label_generator import generate_labels_from_structured_firs
from ai_engine.data.legal_corpus import LEGAL_CORPUS
from ai_engine.models.classifier import (
    FirClassifierModel, FirVocabulary, CrimeLabels
)


# ══════════════════ DATA AUGMENTATION ══════════════════

def augment_from_legal_corpus() -> list:
    """
    Generate synthetic training examples from the legal corpus.
    Each legal section's description + example becomes a training example.
    """
    synthetic = []
    for section in LEGAL_CORPUS:
        # Use description as a narrative
        synthetic.append({
            "narrative": section["description"],
            "crime_type": section["crime_type"],
            "severity": section["severity"],
            "source": "legal_corpus_description",
        })
        # Use example scenario
        if section.get("example_scenario"):
            synthetic.append({
                "narrative": section["example_scenario"],
                "crime_type": section["crime_type"],
                "severity": section["severity"],
                "source": "legal_corpus_example",
            })
        # Combine title + elements as a short narrative
        elements_text = f"{section['title']}. Elements: {', '.join(section.get('elements', []))}"
        synthetic.append({
            "narrative": elements_text,
            "crime_type": section["crime_type"],
            "severity": section["severity"],
            "source": "legal_corpus_elements",
        })
    return synthetic


def augment_shuffle_words(narrative: str) -> str:
    """Augment by randomly shuffling word order in sentences."""
    words = narrative.split()
    if len(words) < 5:
        return narrative
    # Shuffle a random segment
    start = random.randint(0, max(0, len(words) - 5))
    end = min(start + random.randint(3, 7), len(words))
    segment = words[start:end]
    random.shuffle(segment)
    words[start:end] = segment
    return " ".join(words)


def augment_drop_words(narrative: str, drop_rate: float = 0.15) -> str:
    """Augment by randomly dropping words."""
    words = narrative.split()
    if len(words) < 5:
        return narrative
    kept = [w for w in words if random.random() > drop_rate]
    return " ".join(kept) if kept else narrative


def augment_dataset(labeled_data: list, target_per_class: int = 30) -> list:
    """
    Augment dataset so each crime type has at least `target_per_class` examples.
    Uses word shuffling, word dropping, legal corpus, AND parsed law PDFs.
    """
    # Add legal corpus examples
    augmented = list(labeled_data)
    augmented.extend(augment_from_legal_corpus())

    # Add parsed law PDF training data (if available)
    law_data_path = os.path.join(
        BACKEND_DIR, "ai_engine", "data", "datasets", "law_training_data.json"
    )
    if os.path.exists(law_data_path):
        with open(law_data_path, "r", encoding="utf-8") as f:
            law_data = json.load(f)
        augmented.extend(law_data)
        print(f"  Added {len(law_data)} examples from parsed law PDFs")

    # Count per class
    counts = Counter(d["crime_type"] for d in augmented)

    # Augment underrepresented classes
    for crime_type, count in counts.items():
        if count >= target_per_class:
            continue

        # Find examples of this class
        examples = [d for d in augmented if d["crime_type"] == crime_type]
        needed = target_per_class - count

        for i in range(needed):
            base = random.choice(examples)
            narr = base["narrative"]

            # Apply random augmentation
            aug_type = random.choice(["shuffle", "drop", "both"])
            if aug_type == "shuffle":
                narr = augment_shuffle_words(narr)
            elif aug_type == "drop":
                narr = augment_drop_words(narr)
            else:
                narr = augment_drop_words(augment_shuffle_words(narr))

            augmented.append({
                "narrative": narr,
                "crime_type": base["crime_type"],
                "severity": base["severity"],
                "source": f"augmented_{aug_type}",
            })

    return augmented


# ══════════════════ PYTORCH DATASET ══════════════════

class FIRDataset(Dataset):
    """PyTorch dataset for FIR narratives."""

    def __init__(self, data: list, vocab: FirVocabulary, labels: CrimeLabels, max_len: int = 256):
        self.data = data
        self.vocab = vocab
        self.labels = labels
        self.max_len = max_len

    def __len__(self):
        return len(self.data)

    def __getitem__(self, idx):
        item = self.data[idx]
        x = torch.tensor(self.vocab.encode(item["narrative"], self.max_len), dtype=torch.long)
        crime_y = torch.tensor(self.labels.encode_crime(item["crime_type"]), dtype=torch.long)
        sev_y = torch.tensor(self.labels.encode_severity(item["severity"]), dtype=torch.long)
        return x, crime_y, sev_y


# ══════════════════ TRAINING LOOP ══════════════════

def train(args):
    print("=" * 60)
    print("  FirAI — Custom Crime Classifier Training")
    print("  100% custom built. No Gemini. No third-party AI.")
    print("=" * 60)

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"\nDevice: {device}")
    if device.type == "cuda":
        print(f"GPU: {torch.cuda.get_device_name(0)}")

    # ── Step 1: Generate labels from FIR data ──
    print("\n[Step 1] Generating labels from IPC/BNS sections...")
    labeled = generate_labels_from_structured_firs(args.data_dir)
    print(f"  Labeled FIRs: {len(labeled)}")

    # ── Step 2: Augment data ──
    print("\n[Step 2] Augmenting training data...")
    augmented = augment_dataset(labeled, target_per_class=args.target_per_class)
    print(f"  Total training examples: {len(augmented)}")

    crimes = Counter(d["crime_type"] for d in augmented)
    print("  Distribution:")
    for ct, count in crimes.most_common():
        print(f"    {ct}: {count}")

    # ── Step 3: Build vocabulary ──
    print("\n[Step 3] Building vocabulary...")
    vocab = FirVocabulary(max_vocab_size=args.vocab_size)
    all_narratives = [d["narrative"] for d in augmented]
    vocab.build_vocab(all_narratives)

    labels = CrimeLabels()

    # ── Step 4: Split data ──
    random.shuffle(augmented)
    split = int(0.85 * len(augmented))
    train_data = augmented[:split]
    val_data = augmented[split:]
    print(f"\n[Step 4] Split: {len(train_data)} train, {len(val_data)} validation")

    train_dataset = FIRDataset(train_data, vocab, labels, max_len=args.max_len)
    val_dataset = FIRDataset(val_data, vocab, labels, max_len=args.max_len)

    train_loader = DataLoader(train_dataset, batch_size=args.batch_size, shuffle=True)
    val_loader = DataLoader(val_dataset, batch_size=args.batch_size)

    # ── Step 5: Create model ──
    model_config = {
        "embed_dim": args.embed_dim,
        "hidden_size": args.hidden_size,
        "num_layers": args.num_layers,
        "dropout": args.dropout,
    }

    model = FirClassifierModel(
        vocab_size=len(vocab.word2idx),
        num_crimes=labels.num_crimes,
        num_severities=labels.num_severities,
        **model_config
    ).to(device)

    total_params = sum(p.numel() for p in model.parameters())
    trainable_params = sum(p.numel() for p in model.parameters() if p.requires_grad)
    print(f"\n[Step 5] Model created")
    print(f"  Total parameters: {total_params:,}")
    print(f"  Trainable parameters: {trainable_params:,}")

    # ── Step 6: Train ──
    optimizer = torch.optim.Adam(model.parameters(), lr=args.lr, weight_decay=1e-5)
    scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(optimizer, patience=5, factor=0.5)
    crime_criterion = nn.CrossEntropyLoss()
    sev_criterion = nn.CrossEntropyLoss()

    best_val_acc = 0.0
    print(f"\n[Step 6] Training for {args.epochs} epochs...")
    print("-" * 60)

    for epoch in range(1, args.epochs + 1):
        # Train
        model.train()
        total_loss = 0
        correct_crime = 0
        correct_sev = 0
        total = 0

        for x, crime_y, sev_y in train_loader:
            x, crime_y, sev_y = x.to(device), crime_y.to(device), sev_y.to(device)

            crime_logits, sev_logits, _ = model(x)
            loss_crime = crime_criterion(crime_logits, crime_y)
            loss_sev = sev_criterion(sev_logits, sev_y)
            loss = loss_crime + 0.5 * loss_sev  # Crime type is primary task

            optimizer.zero_grad()
            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
            optimizer.step()

            total_loss += loss.item()
            correct_crime += (crime_logits.argmax(1) == crime_y).sum().item()
            correct_sev += (sev_logits.argmax(1) == sev_y).sum().item()
            total += len(x)

        train_acc = correct_crime / total
        train_sev_acc = correct_sev / total

        # Validate
        model.eval()
        val_correct_crime = 0
        val_correct_sev = 0
        val_total = 0
        val_loss = 0

        with torch.no_grad():
            for x, crime_y, sev_y in val_loader:
                x, crime_y, sev_y = x.to(device), crime_y.to(device), sev_y.to(device)
                crime_logits, sev_logits, _ = model(x)
                loss = crime_criterion(crime_logits, crime_y) + 0.5 * sev_criterion(sev_logits, sev_y)
                val_loss += loss.item()
                val_correct_crime += (crime_logits.argmax(1) == crime_y).sum().item()
                val_correct_sev += (sev_logits.argmax(1) == sev_y).sum().item()
                val_total += len(x)

        val_acc = val_correct_crime / max(val_total, 1)
        val_sev_acc = val_correct_sev / max(val_total, 1)
        avg_val_loss = val_loss / max(len(val_loader), 1)
        scheduler.step(avg_val_loss)

        if epoch % 5 == 0 or epoch == 1:
            print(f"  Epoch {epoch:3d}/{args.epochs} | "
                  f"Loss: {total_loss/len(train_loader):.4f} | "
                  f"Train Crime: {train_acc:.1%} Sev: {train_sev_acc:.1%} | "
                  f"Val Crime: {val_acc:.1%} Sev: {val_sev_acc:.1%}")

        # Save best model
        if val_acc > best_val_acc:
            best_val_acc = val_acc
            best_state = model.state_dict()

    print("-" * 60)
    print(f"  Best validation crime accuracy: {best_val_acc:.1%}")

    # ── Step 7: Save model ──
    out_dir = args.output_dir
    os.makedirs(out_dir, exist_ok=True)

    model_path = os.path.join(out_dir, "classifier.pt")
    torch.save({
        "model_state_dict": best_state,
        "model_config": model_config,
        "vocab_size": len(vocab.word2idx),
        "num_crimes": labels.num_crimes,
        "num_severities": labels.num_severities,
        "best_val_acc": best_val_acc,
        "crime_types": labels.CRIME_TYPES,
        "severity_levels": labels.SEVERITY_LEVELS,
    }, model_path)

    vocab_path = os.path.join(out_dir, "classifier_vocab.pkl")
    vocab.save(vocab_path)

    print(f"\n[Step 7] Model saved!")
    print(f"  Model:      {model_path} ({os.path.getsize(model_path)/1024:.0f} KB)")
    print(f"  Vocabulary: {vocab_path} ({os.path.getsize(vocab_path)/1024:.0f} KB)")
    print(f"\nDone! Copy these files to backend/ai_engine/trained_models/")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Train FirAI Crime Classifier")
    parser.add_argument("--data_dir", type=str,
                        default=os.path.join(BACKEND_DIR, "data", "structured"),
                        help="Path to structured FIR JSON directory")
    parser.add_argument("--output_dir", type=str,
                        default=os.path.join(BACKEND_DIR, "ai_engine", "trained_models"),
                        help="Where to save trained model")
    parser.add_argument("--epochs", type=int, default=50)
    parser.add_argument("--batch_size", type=int, default=8)
    parser.add_argument("--lr", type=float, default=0.001)
    parser.add_argument("--embed_dim", type=int, default=128)
    parser.add_argument("--hidden_size", type=int, default=128)
    parser.add_argument("--num_layers", type=int, default=2)
    parser.add_argument("--dropout", type=float, default=0.3)
    parser.add_argument("--vocab_size", type=int, default=8000)
    parser.add_argument("--max_len", type=int, default=256)
    parser.add_argument("--target_per_class", type=int, default=30,
                        help="Minimum examples per crime type after augmentation")

    args = parser.parse_args()
    train(args)
