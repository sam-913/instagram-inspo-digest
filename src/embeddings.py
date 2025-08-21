# src/embeddings.py
from functools import lru_cache
from typing import List
import numpy as np

_MODEL = None

def _get_model():
    global _MODEL
    if _MODEL is not None:
        return _MODEL
    from sentence_transformers import SentenceTransformer
    # Tiny, fast, 384-dim
    _MODEL = SentenceTransformer("all-MiniLM-L6-v2")
    return _MODEL

@lru_cache(maxsize=2048)
def embed_text_cached(text: str) -> List[float]:
    if not text or not text.strip():
        return []
    model = _get_model()
    vec: np.ndarray = model.encode([text.strip()], normalize_embeddings=True)[0]
    return vec.astype(float).tolist()

def embed_many(texts: List[str]) -> List[List[float]]:
    model = _get_model()
    cleaned = [t.strip() for t in texts if isinstance(t, str) and t.strip()]
    if not cleaned:
        return []
    vecs: np.ndarray = model.encode(cleaned, normalize_embeddings=True)
    return [v.astype(float).tolist() for v in vecs]
