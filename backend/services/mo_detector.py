"""
MO (Modus Operandi) Detector Service
--------------------------------------
Detects recurring crime patterns across FIR narratives
using embedding clustering and Gemini analysis.
"""

from typing import List, Optional
from services.embedding_engine import embedding_engine
from services import gemini_service
import numpy as np
from sklearn.cluster import DBSCAN


async def detect_patterns_from_narratives(narratives: List[dict]) -> list:
    """
    Detect MO patterns from a list of FIR narrative dicts.
    Each dict should have 'id', 'narrative', and optionally 'crime_type'.

    Uses both embedding clustering and Gemini analysis.
    """
    if not narratives:
        return []

    # Method 1: Use Gemini for intelligent pattern detection
    narrative_texts = [n.get("narrative", "") for n in narratives if n.get("narrative")]
    gemini_patterns = await gemini_service.detect_mo_patterns(narrative_texts)

    # Method 2: Embedding-based clustering for additional pattern detection
    cluster_patterns = _cluster_narratives(narratives)

    # Merge results
    all_patterns = []

    for p in gemini_patterns:
        all_patterns.append({
            "pattern_name": p.get("pattern_name", "Unknown Pattern"),
            "description": p.get("description", ""),
            "crime_type": p.get("crime_type", ""),
            "occurrence_count": p.get("occurrence_count", 0),
            "linked_fir_ids": p.get("linked_firs", []),
            "source": "gemini"
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
    """
    if len(narratives) < 3:
        return []

    try:
        texts = [n.get("narrative", "") for n in narratives if n.get("narrative")]
        ids = [n.get("id", i) for i, n in enumerate(narratives) if n.get("narrative")]

        if len(texts) < 3:
            return []

        embeddings = embedding_engine.encode_narratives(texts)

        # DBSCAN clustering on embeddings
        clustering = DBSCAN(eps=0.5, min_samples=2, metric='cosine')
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
                "description": f"Group of {len(members)} FIRs with similar narrative patterns",
                "crime_type": "mixed",
                "occurrence_count": len(members),
                "linked_fir_ids": [m["id"] for m in members],
            })

        return patterns

    except Exception as e:
        print(f"[MODetector] Clustering error: {e}")
        return []
