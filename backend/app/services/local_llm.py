"""Local LLM relevance judge — MLX on Apple Silicon (in-process, no keys, offline).

The embedding scorer retrieves; this decides. For each candidate the LLM reads the
program's synopsis against the startup profile and returns a structured verdict:
relevance 0-100, fit tier, one-line reason, and whether a for-profit startup could
realistically apply. Verdicts blend with the embedding score in matching.py.

Backends, in order: MLX (mlx-lm, Metal GPU, ~0.6s/judgment on M-series) → Ollama
(if MLX unavailable) → no-op. The pipeline never depends on any of them.
"""
from __future__ import annotations

import asyncio
import json
import logging
import os
import re
import threading
from typing import Optional

from ..models import StartupProfile

log = logging.getLogger(__name__)

MLX_MODEL = os.environ.get("MLX_MODEL", "mlx-community/Qwen3-4B-4bit")
OLLAMA_URL = os.environ.get("OLLAMA_URL", "http://localhost:11434")
OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL", "qwen3:4b")
DISABLED = os.environ.get("LOCAL_LLM", "on").lower() in ("off", "0", "false")
MAX_TOKENS = 260

SYSTEM = (
    "You are a federal funding analyst. Judge whether ONE government program is relevant "
    "for ONE startup. Be strict and honest: topical keyword overlap is not relevance. "
    "likely_fit = the program funds the startup's actual kind of work AND 'Small business may apply' "
    "is YES — when it is YES, do not hedge about eligibility. potential_fit = topically right but eligibility unclear or partnership "
    "needed. adjacent = related theme, different purpose or audience. not_a_fit = programs for "
    "foreign audiences, public diplomacy, unrelated sectors, or clearly non-business recipients. "
    "Return ONLY a JSON object with keys: relevance (integer 0-100), "
    "fit_tier (one of likely_fit, potential_fit, adjacent, not_a_fit), "
    "startup_can_apply (boolean), reason (ONE short sentence, max 25 words)."
)

_backend: Optional[str] = None  # "mlx" | "ollama" | "none"


def _cache_key(profile_text: str, cand: dict) -> str:
    """A verdict is a pure function of (profile, program text) — cache it in Mongo so
    repeated matches for similar companies skip the GPU entirely."""
    import hashlib

    blob = "|".join([
        "v2", MLX_MODEL, profile_text, str(cand.get("source_id")), (cand.get("summary") or "")[:1200],
        ",".join(cand.get("eligible_applicants") or []), str(cand.get("eligibility_flag")),
    ])
    return hashlib.sha256(blob.encode()).hexdigest()


def _cache_get(keys: list[str]) -> dict[str, dict]:
    try:
        from .store import _db

        return {d["_id"]: d["verdict"] for d in _db().llm_verdicts.find({"_id": {"$in": keys}})}
    except Exception:
        return {}


def _cache_put(items: dict[str, dict]) -> None:
    if not items:
        return
    try:
        from datetime import datetime, timezone

        from .store import _db

        col = _db().llm_verdicts
        now = datetime.now(timezone.utc).isoformat()
        for k, v in items.items():
            col.update_one({"_id": k}, {"$set": {"verdict": v, "model": MLX_MODEL, "at": now}}, upsert=True)
    except Exception:
        log.exception("llm verdict cache write failed")
_mlx = None  # (model, tokenizer)
_mlx_lock = threading.Lock()  # MLX generation is not thread-safe; serialize calls
_init_lock = threading.Lock()


def _init_backend() -> str:
    global _backend, _mlx
    if _backend is not None:
        return _backend
    with _init_lock:
        if _backend is not None:
            return _backend
        if DISABLED:
            _backend = "none"
            return _backend
        try:
            from mlx_lm import load

            _mlx = load(MLX_MODEL)
            _backend = "mlx"
            log.info("local LLM: MLX backend ready (%s)", MLX_MODEL)
            return _backend
        except Exception as e:
            log.info("local LLM: MLX unavailable (%s: %s); trying Ollama", type(e).__name__, str(e)[:80])
        try:
            import httpx

            r = httpx.get(f"{OLLAMA_URL}/api/tags", timeout=3)
            names = [m.get("name", "") for m in r.json().get("models", [])]
            if any(n.split(":")[0] == OLLAMA_MODEL.split(":")[0] for n in names):
                _backend = "ollama"
                log.info("local LLM: Ollama backend ready (%s)", OLLAMA_MODEL)
                return _backend
        except Exception:
            pass
        _backend = "none"
        log.info("local LLM: no backend available; relevance judge disabled")
        return _backend


def warmup() -> None:
    _init_backend()


def provider_name() -> str:
    b = _backend or "uninitialized"
    return {"mlx": f"mlx:{MLX_MODEL.split('/')[-1]}", "ollama": f"ollama:{OLLAMA_MODEL}"}.get(
        b, "embeddings+rules"
    )


def _elig_word(flag) -> str:
    return {"ok": "YES (listed explicitly)", "likely_ineligible": "NO (not on applicant list)"}.get(flag, "UNCLEAR")


def _prompt_for(profile_text: str, cand: dict) -> str:
    return (
        f"STARTUP:\n{profile_text}\n\n"
        f"PROGRAM:\nTitle: {cand.get('title','')}\nAgency: {cand.get('agency','')}\n"
        f"Eligible applicants (official, authoritative): {', '.join(cand.get('eligible_applicants') or []) or 'not stated'}\n"
        f"Small business may apply: {_elig_word(cand.get('eligibility_flag'))}\n"
        f"Synopsis: {(cand.get('summary') or '')[:1200]}\n\n"
        "Judge relevance for this startup."
    )


def _parse(raw: str) -> Optional[dict]:
    raw = re.sub(r"<think>.*?</think>", "", raw, flags=re.S)
    m = re.search(r"\{.*\}", raw, flags=re.S)
    if m:
        try:
            return json.loads(m.group(0))
        except json.JSONDecodeError:
            pass
    # salvage a truncated object: the numeric/enum fields come first
    out: dict = {}
    if r := re.search(r'"relevance"\s*:\s*(\d+)', raw):
        out["relevance"] = int(r.group(1))
    if t := re.search(r'"fit_tier"\s*:\s*"([a-z_]+)"', raw):
        out["fit_tier"] = t.group(1)
    if a := re.search(r'"startup_can_apply"\s*:\s*(true|false)', raw):
        out["startup_can_apply"] = a.group(1) == "true"
    if s := re.search(r'"reason"\s*:\s*"([^"]*)', raw):
        out["reason"] = s.group(1)
    return out if "relevance" in out and "fit_tier" in out else None


def _judge_mlx(profile_text: str, cand: dict) -> Optional[dict]:
    from mlx_lm import generate

    model, tok = _mlx
    msgs = [{"role": "system", "content": SYSTEM}, {"role": "user", "content": _prompt_for(profile_text, cand)}]
    prompt = tok.apply_chat_template(msgs, tokenize=False, add_generation_prompt=True, enable_thinking=False)
    with _mlx_lock:
        out = generate(model, tok, prompt=prompt, max_tokens=MAX_TOKENS, verbose=False)
    return _parse(out)


def _judge_ollama(profile_text: str, cand: dict) -> Optional[dict]:
    import httpx

    schema = {
        "type": "object",
        "properties": {
            "relevance": {"type": "integer"}, "fit_tier": {"type": "string"},
            "startup_can_apply": {"type": "boolean"}, "reason": {"type": "string"},
        },
        "required": ["relevance", "fit_tier", "startup_can_apply", "reason"],
    }
    r = httpx.post(
        f"{OLLAMA_URL}/api/generate",
        json={
            "model": OLLAMA_MODEL, "system": SYSTEM, "prompt": _prompt_for(profile_text, cand),
            "format": schema, "stream": False, "think": False,
            "options": {"temperature": 0, "num_predict": MAX_TOKENS},
        },
        timeout=30,
    )
    r.raise_for_status()
    return _parse(r.json().get("response", ""))


def _judge_sync(profile_text: str, cand: dict) -> Optional[dict]:
    try:
        if _backend == "mlx":
            return _judge_mlx(profile_text, cand)
        if _backend == "ollama":
            return _judge_ollama(profile_text, cand)
    except Exception as e:
        log.info("local LLM judge skipped for %s: %s", cand.get("source_id"), type(e).__name__)
    return None


async def judge(profile: StartupProfile, candidates: list[dict]) -> dict[str, dict]:
    """Returns {source_id: verdict} for candidates the LLM managed to judge."""
    if not candidates:
        return {}
    backend = await asyncio.to_thread(_init_backend)
    if backend == "none":
        return {}
    profile_text = json.dumps(
        {k: v for k, v in profile.model_dump().items() if v not in (None, "", [])}, ensure_ascii=False
    )
    keys = {c["source_id"]: _cache_key(profile_text, c) for c in candidates}
    cached = await asyncio.to_thread(_cache_get, list(keys.values()))
    out: dict[str, dict] = {c["source_id"]: cached[keys[c["source_id"]]] for c in candidates if keys[c["source_id"]] in cached}
    todo = [c for c in candidates if c["source_id"] not in out]
    log.info("llm judge: %d cached, %d to run", len(out), len(todo))

    # MLX serializes on the GPU anyway; Ollama benefits from a little parallelism
    if backend == "mlx":
        results = [await asyncio.to_thread(_judge_sync, profile_text, c) for c in todo]
    else:
        sem = asyncio.Semaphore(4)

        async def run(c):
            async with sem:
                return await asyncio.to_thread(_judge_sync, profile_text, c)

        results = await asyncio.gather(*(run(c) for c in todo))
    fresh = {c["source_id"]: v for c, v in zip(todo, results) if v}
    await asyncio.to_thread(_cache_put, {keys[sid]: v for sid, v in fresh.items()})
    out.update(fresh)
    return out
