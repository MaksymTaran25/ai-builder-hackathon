"""In-memory embedding index over the whole warehouse, so a match can score every
program (1.7K) in ~1ms instead of re-embedding. Rebuilt lazily when the warehouse
changes (checked by count + latest harvest time)."""
from __future__ import annotations

import logging
import threading

import numpy as np

from . import embeddings, store

log = logging.getLogger(__name__)

_lock = threading.Lock()
_docs: list[dict] = []
_vecs: np.ndarray | None = None
_stamp: tuple = ()


def _current_stamp() -> tuple:
    try:
        db = store._db()
        n = db.opportunities.count_documents({"source": "grants_gov", "archived_at": {"$exists": False}})
        last = db.harvest_runs.find_one(sort=[("started_at", -1)]) or {}
        return (n, last.get("started_at", ""))
    except Exception:
        return (0, "")


def _rebuild() -> None:
    global _docs, _vecs, _stamp
    docs = store.all_live_opportunities()
    texts = [f"{d.get('title','')}. {(d.get('summary') or '')[:600]}" for d in docs]
    vecs = embeddings.embed(texts) if texts else np.zeros((0, 384))
    _docs, _vecs, _stamp = docs, vecs, _current_stamp()
    log.info("warehouse index: %d programs embedded", len(docs))


def ensure() -> None:
    with _lock:
        if _vecs is None or _current_stamp() != _stamp:
            _rebuild()


def score_all(query: str) -> list[tuple[dict, float]]:
    """(doc, cosine) for every program in the warehouse, best first."""
    ensure()
    if _vecs is None or len(_docs) == 0:
        return []
    q = embeddings.embed([query])[0]
    sims = _vecs @ q
    order = np.argsort(-sims)
    return [(_docs[i], float(sims[i])) for i in order]
