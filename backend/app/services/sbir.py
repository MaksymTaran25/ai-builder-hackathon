"""SBIR/STTR award history from local MongoDB (official bulk data, 2018+).

The live SBIR API is down for maintenance (Aug 2026), so awards come from the
official bulk CSV ingested by app.ingest.sbir_ingest. Used two ways:
1. history stats for "who got funded for similar technology"
2. synthesized "SBIR/STTR pathway" opportunity cards per top funding agency

If mongod is unreachable, every function degrades to empty results — the app
keeps working without the SBIR slice (same contract as a live-API outage).
"""
from __future__ import annotations

import logging
import os
import re
import statistics
import threading
from typing import Optional

from ..models import HistoricalStats, Opportunity

log = logging.getLogger(__name__)

MONGO_URL = os.environ.get("MONGO_URL", "mongodb://localhost:27017")

_client = None
_lock = threading.Lock()

AGENCY_SBIR_LINKS = {
    "Department of Health and Human Services": "https://seed.nih.gov/",
    "National Science Foundation": "https://seedfund.nsf.gov/",
    "Department of War": "https://www.dodsbirsttr.mil/",
    "Department of Defense": "https://www.dodsbirsttr.mil/",
    "National Aeronautics and Space Administration": "https://sbir.nasa.gov/",
    "Department of Energy": "https://science.osti.gov/sbir",
    "Department of Homeland Security": "https://www.dhs.gov/science-and-technology/sbir",
    "Environmental Protection Agency": "https://www.epa.gov/sbir",
    "United States Dept. of Agriculture": "https://www.nifa.usda.gov/grants/programs/sbir-sttr",
}


def _col():
    global _client
    if _client is None:
        with _lock:
            if _client is None:
                from pymongo import MongoClient

                _client = MongoClient(MONGO_URL, serverSelectionTimeoutMS=1500)
    return _client.govmatch.sbir_awards


_PROJECTION = {
    "_id": 0, "company": 1, "title": 1, "agency": 1, "phase": 1,
    "program": 1, "award_year": 1, "award_amount": 1, "state": 1,
    "city": 1, "score": {"$meta": "textScore"},
}


def similar_awards(topics: list[str], state: Optional[str], limit: int = 400) -> list[dict]:
    """OR-of-phrases retrieval: one $text query per topic phrase (quoted = exact
    phrase match), merged by max score. Mirrors the tight topical semantics we
    want — a single stray word shouldn't match."""
    phrases = []
    for t in topics:
        clean = re.sub(r"[^a-zA-Z0-9 ]", " ", t).strip().lower()
        if clean and clean not in phrases:
            phrases.append(clean)
    if not phrases:
        return []

    merged: dict[tuple, dict] = {}
    per_phrase = max(80, limit // len(phrases))
    try:
        col = _col()
        for p in phrases:
            for r in (
                col.find({"$text": {"$search": f'"{p}"'}}, _PROJECTION)
                .sort([("score", {"$meta": "textScore"})])
                .limit(per_phrase)
            ):
                key = (r.get("company"), r.get("title"), r.get("award_year"))
                if key not in merged or r["score"] > merged[key]["score"]:
                    merged[key] = r
    except Exception:
        log.exception("Mongo text search failed (is mongod running?)")
        return []
    return sorted(merged.values(), key=lambda r: r["score"], reverse=True)[:limit]


def search_awards(search: str, state: Optional[str], limit: int = 20) -> list[dict]:
    """Warehouse search: free-text over the corpus, optional hard state filter."""
    terms = re.sub(r"[^a-zA-Z0-9 ]", " ", search).strip()
    if not terms:
        return []
    q: dict = {"$text": {"$search": terms}}
    if state:
        q["state"] = state
    try:
        return list(
            _col()
            .find(q, _PROJECTION)
            .sort([("score", {"$meta": "textScore"})])
            .limit(limit)
        )
    except Exception:
        log.exception("Mongo warehouse search failed")
        return []


def history_for_topics(topics: list[str], state: Optional[str]) -> Optional[HistoricalStats]:
    rows = similar_awards(topics, state)
    if not rows:
        return None
    return _stats(rows, state)


def _stats(rows: list[dict], state: Optional[str], agency_short: Optional[str] = None) -> HistoricalStats:
    amounts = [r["award_amount"] for r in rows if r.get("award_amount")]
    in_state = [r for r in rows if state and r.get("state") == state]
    ordered = in_state + [r for r in rows if not (state and r.get("state") == state)]
    return HistoricalStats(
        similar_companies=len({r["company"] for r in rows}),
        total_awarded_usd=float(sum(amounts)),
        median_award_usd=float(statistics.median(amounts)) if amounts else 0,
        in_state_recipients=len({r["company"] for r in in_state}),
        sample_recipients=[
            {
                "name": (r.get("company") or "").title(),
                "agency": agency_short or _short_agency(r.get("agency") or ""),
                "amount": r.get("award_amount"),
                "year": r.get("award_year"),
                "program": f"{r.get('program', '')} {r.get('phase', '')}".strip(),
            }
            for r in ordered[:5]
        ],
    )


def _short_agency(a: str) -> str:
    return {
        "Department of Health and Human Services": "HHS",
        "National Science Foundation": "NSF",
        "Department of War": "DOW",
        "Department of Defense": "DOD",
        "National Aeronautics and Space Administration": "NASA",
        "Department of Energy": "DOE",
        "Department of Homeland Security": "DHS",
        "Environmental Protection Agency": "EPA",
        "United States Dept. of Agriculture": "USDA",
        "Department of Commerce": "DOC",
        "Department of Transportation": "DOT",
        "Department of Education": "ED",
    }.get(a, a)


def pathway_opportunities(topics: list[str], state: Optional[str], max_agencies: int = 2) -> list[Opportunity]:
    """Synthesize an 'SBIR/STTR pathway' card for the agencies that most fund this tech."""
    rows = similar_awards(topics, state)
    if not rows:
        return []
    by_agency: dict[str, list[dict]] = {}
    for r in rows:
        by_agency.setdefault(r.get("agency") or "", []).append(r)
    ranked = sorted(by_agency.items(), key=lambda kv: len(kv[1]), reverse=True)[:max_agencies]

    opps: list[Opportunity] = []
    for agency, ars in ranked:
        short = _short_agency(agency)
        opps.append(
            Opportunity(
                source="sbir",
                source_id=f"sbir-{short.lower()}",
                title=f"SBIR/STTR — {short} America's Seed Fund pathway",
                agency=agency,
                program="SBIR/STTR",
                status="recurring program",
                url=AGENCY_SBIR_LINKS.get(agency, "https://www.sbir.gov/topics"),
                summary=(
                    f"{short} has made {len(ars)} SBIR/STTR awards since 2018 for technology similar "
                    f"to yours. Phase I typically ~$150K-$300K, Phase II up to ~$1M-$2M, non-dilutive."
                ),
                history=_stats(ars, state, agency_short=short),
            )
        )
    return opps
