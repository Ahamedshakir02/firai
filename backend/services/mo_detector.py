"""
MO (Modus Operandi) Detector Service
--------------------------------------
Detects recurring crime patterns across FIR narratives
using embedding clustering and FirAI Engine classification.
"""

from typing import List, Optional
from services.embedding_engine import embedding_engine, strip_fir_boilerplate
from services import firai_engine
import numpy as np
from sklearn.cluster import DBSCAN


async def detect_patterns_from_narratives(narratives: List[dict]) -> list:
    """
    Detect MO patterns from a list of FIR narrative dicts.
    Each dict should have 'id', 'narrative', and optionally 'crime_type'.

    Uses both embedding clustering and FirAI Engine classification.
    Strips FIR boilerplate first so patterns are based on actual crime content,
    not shared FIR template format.
    """
    if not narratives:
        return []

    # Strip boilerplate from all narratives before analysis
    cleaned_narratives = []
    for n in narratives:
        raw = n.get("narrative", "")
        cleaned = strip_fir_boilerplate(raw) if raw else ""
        cleaned_narratives.append(cleaned)

    # Method 1: Use FirAI Engine for pattern detection
    firai_patterns = await firai_engine.detect_mo_patterns(cleaned_narratives)

    # Method 2: Embedding-based clustering for additional pattern detection
    cluster_input = [
        {"id": n.get("id", i), "narrative": cleaned_narratives[i], "crime_type": n.get("crime_type")}
        for i, n in enumerate(narratives)
        if cleaned_narratives[i]  # skip empty cleaned narratives
    ]
    cluster_patterns = _cluster_narratives(cluster_input)

    # Merge results
    all_patterns = []

    for p in firai_patterns:
        all_patterns.append({
            "pattern_name": p.get("pattern_name", "Unknown Pattern"),
            "description": p.get("description", ""),
            "crime_type": p.get("crime_type", ""),
            "occurrence_count": p.get("occurrence_count", 0),
            "linked_fir_ids": p.get("linked_firs", []),
            "source": "firai_engine"
        })

    for p in cluster_patterns:
        all_patterns.append({
            "pattern_name": p.get("pattern_name", "Cluster Pattern"),
            "description": p.get("description", ""),
            "crime_type": p.get("crime_type", ""),
            "occurrence_count": p.get("occurrence_count", 0),
            "linked_fir_ids": p.get("linked_fir_ids", []),
            "source": "clustering"
        })

    return all_patterns


def _cluster_narratives(narratives: List[dict]) -> list:
    """
    Use DBSCAN clustering on narrative embeddings to find similar crime groups.
    Narratives should already be stripped of boilerplate.
    """
    if len(narratives) < 3:
        return []

    try:
        texts = [n.get("narrative", "") for n in narratives if n.get("narrative")]
        ids = [n.get("id", i) for i, n in enumerate(narratives) if n.get("narrative")]

        if len(texts) < 3:
            return []

        # Embeddings are already cleaned by encode_narratives (strips boilerplate internally)
        embeddings = embedding_engine.encode_narratives(texts)

        # DBSCAN clustering on embeddings
        # eps=0.35 requires higher similarity (lower distance) to cluster together
        # This prevents unrelated FIRs from being grouped just because of format similarity
        clustering = DBSCAN(eps=0.35, min_samples=2, metric='cosine')
        labels = clustering.fit_predict(embeddings)

        # Group by cluster
        clusters = {}
        for idx, label in enumerate(labels):
            if label == -1:  # Noise points
                continue
            if label not in clusters:
                clusters[label] = []
            clusters[label].append({"id": ids[idx], "narrative": texts[idx][:200]})

        patterns = []
        for cluster_id, members in clusters.items():
            patterns.append({
                "pattern_name": f"Crime Cluster #{cluster_id + 1}",
                "description": f"Group of {len(members)} FIRs with similar crime methods and patterns",
                "crime_type": "mixed",
                "occurrence_count": len(members),
                "linked_fir_ids": [m["id"] for m in members],
            })

        return patterns

    except Exception as e:
        print(f"[MODetector] Clustering error: {e}")
        return []
