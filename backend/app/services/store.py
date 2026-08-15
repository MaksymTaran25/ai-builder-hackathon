"""MongoDB warehouse: everything fetched from government sources is persisted
here, so any other process can query it (via /graphql or pymongo directly).

Collections (db `govmatch`):
  sbir_awards    — bulk SBIR history (written by app.ingest.sbir_ingest)
  opportunities  — every Grants.gov opportunity we fetched details for (upsert by source_id)
  award_history  — USAspending recipient stats per CFDA set + state (upsert)
  match_runs     — every profile + the map it produced (append-only)

Writes are best-effort: mongod being down must never break a match request.
"""
from __future__ import annotations

import logging
import os
import threading
from datetime import datetime, timezone
from typing import Optional

from ..models import HistoricalStats, MatchResponse, Opportunity, StartupProfile

log = logging.getLogger(__name__)

MONGO_URL = os.environ.get("MONGO_URL", "mongodb://localhost:27017")

_client = None
_lock = threading.Lock()


def _db():
    global _client
    if _client is None:
        with _lock:
            if _client is None:
                from pymongo import MongoClient

                _client = MongoClient(MONGO_URL, serverSelectionTimeoutMS=1500)
    return _client.govmatch


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def upsert_opportunities(opps: list[Opportunity]) -> None:
    try:
        col = _db().opportunities
        for o in opps:
            doc = o.model_dump()
            doc["fit_tier"] = o.fit_tier.value
            doc["fetched_at"] = _now()
            col.update_one({"source_id": o.source_id}, {"$set": doc}, upsert=True)
    except Exception:
        log.exception("warehouse: opportunity upsert failed")


def save_history(cfda: list[str], state: Optional[str], stats: HistoricalStats) -> None:
    try:
        key = {"cfda": sorted(cfda), "state": state or ""}
        _db().award_history.update_one(
            key, {"$set": {**key, "stats": stats.model_dump(), "fetched_at": _now()}}, upsert=True
        )
    except Exception:
        log.exception("warehouse: history upsert failed")


def save_match_run(profile: StartupProfile, result: MatchResponse) -> None:
    try:
        _db().match_runs.insert_one({
            "created_at": _now(),
            "profile": profile.model_dump(),
            "summary": result.summary.model_dump(),
            "opportunities": [
                {
                    "source_id": o.source_id, "title": o.title, "agency": o.agency,
                    "score": o.score, "fit_tier": o.fit_tier.value,
                }
                for o in result.opportunities
            ],
            "similar_companies": [c.model_dump() for c in result.similar_companies],
            "agency_map": [a.model_dump() for a in result.agency_map],
        })
    except Exception:
        log.exception("warehouse: match run insert failed")


# ---- read side (used by the GraphQL warehouse queries) ----

def stored_opportunities(
    search: Optional[str],
    limit: int,
    domain: Optional[str] = None,
    eligibility: Optional[str] = None,
    agency: Optional[str] = None,
) -> list[dict]:
    try:
        q: dict = {}
        if search:
            q["$or"] = [
                {"title": {"$regex": search, "$options": "i"}},
                {"agency": {"$regex": search, "$options": "i"}},
                {"summary": {"$regex": search, "$options": "i"}},
            ]
        if domain:
            q["domains"] = domain
        if eligibility:
            q["eligibility_flag"] = eligibility
        if agency:
            q["agency"] = {"$regex": agency, "$options": "i"}
        return list(_db().opportunities.find(q, {"_id": 0}).sort("close_date", 1).limit(limit))
    except Exception:
        log.exception("warehouse: stored_opportunities read failed")
        return []


def harvest_runs(limit: int) -> list[dict]:
    try:
        return list(_db().harvest_runs.find({}, {"_id": 0}).sort("started_at", -1).limit(limit))
    except Exception:
        log.exception("warehouse: harvest_runs read failed")
        return []


def stored_match_runs(limit: int) -> list[dict]:
    try:
        return list(_db().match_runs.find({}, {"_id": 0}).sort("created_at", -1).limit(limit))
    except Exception:
        log.exception("warehouse: match_runs read failed")
        return []


def stored_award_history(limit: int) -> list[dict]:
    try:
        return list(_db().award_history.find({}, {"_id": 0}).sort("fetched_at", -1).limit(limit))
    except Exception:
        log.exception("warehouse: award_history read failed")
        return []
