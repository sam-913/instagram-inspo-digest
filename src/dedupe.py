# src/dedupe.py
from typing import List, Tuple
import numpy as np
from src.embeddings import embed_text_cached

def dedupe_texts(texts: List[str], sim_threshold: float = 0.90) -> Tuple[List[str], List[Tuple[int, int, float]]]:
    """
    Remove near-duplicate texts using cosine similarity on normalized embeddings.
    Returns (unique_texts, dropped_pairs), where dropped_pairs = [(keep_idx, drop_idx, similarity), ...]
    """
    clean = [t.strip() for t in texts if t and t.strip()]
    if not clean:
        return [], []

    vecs = []
    for t in clean:
        v = embed_text_cached(t)
        vecs.append(np.array(v, dtype=float) if v else np.zeros(384, dtype=float))

    keep: List[int] = []
    dropped: List[Tuple[int, int, float]] = []

    for i, v in enumerate(vecs):
        if not v.any():
            continue
        is_dup = False
        for k in keep:
            sim = float(np.dot(v, vecs[k]))  # vectors are normalized in embed_text_cached
            if sim >= sim_threshold:
                dropped.append((k, i, sim))
                is_dup = True
                break
        if not is_dup:
            keep.append(i)

    uniq = [clean[i] for i in keep]
    return uniq, dropped
