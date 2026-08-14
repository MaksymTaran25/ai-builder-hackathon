"""Local semantic similarity via fastembed (BAAI/bge-small-en-v1.5, ONNX, no API)."""
from __future__ import annotations

import threading

import numpy as np

_model = None
_lock = threading.Lock()


def _get_model():
    global _model
    if _model is None:
        with _lock:
            if _model is None:
                from fastembed import TextEmbedding

                _model = TextEmbedding("BAAI/bge-small-en-v1.5")
    return _model


def embed(texts: list[str]) -> np.ndarray:
    """L2-normalized embeddings, shape (n, 384)."""
    model = _get_model()
    vecs = np.array(list(model.embed(texts)))
    norms = np.linalg.norm(vecs, axis=1, keepdims=True)
    return vecs / np.clip(norms, 1e-9, None)


def similarities(query: str, texts: list[str]) -> np.ndarray:
    """Cosine similarity of one query against many texts."""
    if not texts:
        return np.array([])
    vecs = embed([query] + texts)
    return vecs[1:] @ vecs[0]


def warmup() -> None:
    _get_model()
