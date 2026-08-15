"""Nightly harvester: sweep Grants.gov across every domain, enrich each opportunity
(synopsis, award data, applicant-type eligibility), upsert into MongoDB.

This is Server 1's "smart scraper" — it stocks the warehouse so downstream
processes (Server 2) have a full corpus without waiting for user searches.

Usage:
  uv run python -m app.ingest.harvest              # full sweep
  uv run python -m app.ingest.harvest --tag        # also LLM-tag domains (slower)
  uv run python -m app.ingest.harvest --dry-run    # search only, no writes

Runs every midnight via launchd (see scripts/install_nightly.sh). Each run writes
a summary document to the `harvest_runs` collection.
"""
from __future__ import annotations

import argparse
import asyncio
import json
import logging
import sys
import time
from datetime import datetime, timezone

from ..models import Opportunity
from ..services import eligibility, grants_gov, store
from ..services.matching import _grants_hit_to_opp, _num, _strip_html

log = logging.getLogger("harvest")

# Domain -> government-vocabulary keywords. Broad on purpose: the warehouse should
# hold everything a startup in any of these spaces might match against.
DOMAINS: dict[str, list[str]] = {
    "healthcare": ["health information technology", "clinical informatics", "digital health",
                   "hospital operations", "nursing workforce", "medical devices", "telehealth"],
    "ai": ["artificial intelligence", "machine learning", "data science", "autonomous systems"],
    "software": ["software development", "information technology", "cloud computing"],
    "manufacturing": ["advanced manufacturing", "manufacturing technology", "additive manufacturing",
                      "supply chain", "industrial automation"],
    "aerospace_defense": ["aerospace", "aeronautics", "space technology", "lightweight materials",
                          "composites", "defense technology", "dual use technology"],
    "energy": ["clean energy", "energy efficiency", "energy storage", "grid modernization",
               "renewable energy", "critical minerals"],
    "water_environment": ["water resources", "water infrastructure", "water treatment",
                          "environmental technology", "climate resilience", "air quality"],
    "cybersecurity": ["cybersecurity", "information security", "critical infrastructure protection",
                      "threat detection", "secure software"],
    "biotech": ["biotechnology", "drug development", "diagnostics", "genomics", "bioengineering"],
    "agriculture": ["precision agriculture", "agricultural technology", "food systems", "rural development"],
    "education_workforce": ["education technology", "STEM education", "workforce development",
                            "apprenticeship", "career training"],
    "community": ["small business", "economic development", "community development",
                  "youth development", "entrepreneurship"],
    "transportation": ["transportation technology", "electric vehicles", "logistics", "infrastructure"],
    "sensors_iot": ["sensors", "internet of things", "monitoring systems", "robotics"],
    "quantum_semiconductors": ["quantum", "semiconductors", "microelectronics", "photonics"],
}


def _enrich(o: Opportunity, d: dict) -> None:
    syn = d.get("synopsis") or {}
    o.award_floor_usd = _num(syn.get("awardFloor"))
    o.award_ceiling_usd = _num(syn.get("awardCeiling"))
    o.estimated_total_funding_usd = _num(syn.get("estimatedFunding"))
    o.expected_awards = int(_num(syn.get("numberOfAwards")) or 0) or None
    o.cost_sharing = syn.get("costSharing") in (True, "true", "Yes", "yes")
    o.summary = _strip_html(syn.get("synopsisDesc") or "")[:1500]
    if syn.get("responseDateStr"):
        import re

        m = re.match(r"(\d{4})-(\d{2})-(\d{2})", syn["responseDateStr"])
        if m:
            o.close_date = f"{m.group(2)}/{m.group(3)}/{m.group(1)}"
    flag, descs = eligibility.evaluate(syn.get("applicantTypes") or [], o.summary)
    o.eligibility_flag = flag
    o.eligible_applicants = descs[:8]


def _tag_by_keywords(o: Opportunity) -> list[str]:
    """Literal keyword tags (fast, precise, low recall). Combined with embedding tags below."""
    text = f"{o.title} {o.summary}".lower()
    return sorted(dom for dom, kws in DOMAINS.items() if any(k.lower() in text for k in kws))


def _tag_by_embeddings(opps: list[Opportunity], threshold: float = 0.52) -> dict[str, list[str]]:
    """Semantic domain tags: embed every program and every domain description once,
    tag where cosine similarity clears the threshold. One batch, a few seconds for 1.7K."""
    import numpy as np

    from ..services import embeddings

    domain_names = list(DOMAINS)
    domain_texts = [f"{d.replace('_', ' ')}: {', '.join(kws)}" for d, kws in DOMAINS.items()]
    prog_texts = [f"{o.title}. {(o.summary or '')[:600]}" for o in opps]
    dv = embeddings.embed(domain_texts)
    pv = embeddings.embed(prog_texts)
    sims = pv @ dv.T  # (programs, domains)
    out: dict[str, list[str]] = {}
    for o, row in zip(opps, sims):
        tags = [domain_names[j] for j in np.argsort(-row)[:4] if row[j] >= threshold]
        out[o.source_id] = tags
    return out


async def harvest(dry_run: bool = False, tag: bool = False, rows_each: int = 40) -> dict:
    """Full sweep: EVERY posted + forecasted opportunity on Grants.gov, enriched. No cap."""
    t0 = time.time()
    started = datetime.now(timezone.utc).isoformat()

    # 1. the whole universe, paginated (empty keyword = everything)
    hits = await grants_gov.search_all("posted|forecasted")
    log.info("search: full sweep -> %d opportunities (posted + forecasted)", len(hits))
    opps: list[Opportunity] = [_grants_hit_to_opp(h) for h in hits]

    if dry_run:
        return {"found": len(hits), "dry_run": True}

    # 2. enrich every one (batches of 50, concurrent within a batch)
    ids = [o.source_id.removeprefix("gg-") for o in opps]
    details: dict[str, dict] = {}
    for i in range(0, len(ids), 50):
        details.update(await grants_gov.fetch_details_many(ids[i:i + 50]))
        if (i // 50) % 5 == 0 or i + 50 >= len(ids):
            log.info("enriched %d/%d", min(i + 50, len(ids)), len(ids))
    for o in opps:
        d = details.get(o.source_id.removeprefix("gg-"))
        if d:
            _enrich(o, d)

    # 3. domain tags: literal keywords ∪ semantic embeddings (all programs), optional LLM on top
    kw_tags = {o.source_id: _tag_by_keywords(o) for o in opps}
    emb_tags = await asyncio.to_thread(_tag_by_embeddings, opps)
    domains_by_id = {sid: sorted(set(kw_tags.get(sid, [])) | set(emb_tags.get(sid, []))) for sid in kw_tags}
    tagged = 0
    if tag:
        tagged = await _tag_domains(opps, domains_by_id)

    # 4. upsert everything; mark anything no longer on Grants.gov as archived
    await asyncio.to_thread(_upsert_all, opps, domains_by_id)
    archived = await asyncio.to_thread(_archive_missing, {o.source_id for o in opps})

    summary = {
        "started_at": started,
        "finished_at": datetime.now(timezone.utc).isoformat(),
        "seconds": round(time.time() - t0, 1),
        "found": len(hits),
        "enriched": len(details),
        "archived_stale": archived,
        "llm_tagged": tagged,
        "eligibility": _count(opps, "eligibility_flag"),
        "by_domain": {d: sum(1 for v in domains_by_id.values() if d in v) for d in DOMAINS},
        "untagged": sum(1 for v in domains_by_id.values() if not v),
    }
    await asyncio.to_thread(_record_run, summary)
    return summary


def _archive_missing(live_ids: set[str]) -> int:
    """Opportunities in the warehouse that Grants.gov no longer lists: flag, don't delete."""
    from ..services.store import _db, _now

    col = _db().opportunities
    res = col.update_many(
        {"source": "grants_gov", "source_id": {"$nin": list(live_ids)}, "archived_at": {"$exists": False}},
        {"$set": {"archived_at": _now()}},
    )
    return res.modified_count


def _upsert_all(opps: list[Opportunity], domains_by_id: dict[str, list[str]]) -> None:
    from ..services.store import _db, _now

    col = _db().opportunities
    for o in opps:
        doc = o.model_dump()
        doc["fit_tier"] = o.fit_tier.value
        doc["domains"] = domains_by_id.get(o.source_id, [])
        doc["harvested_at"] = _now()
        col.update_one({"source_id": o.source_id}, {"$set": doc}, upsert=True)
    col.create_index("domains")
    col.create_index("agency")
    col.create_index("eligibility_flag")
    col.create_index("archived_at")
    col.create_index([("title", "text"), ("summary", "text")], name="opp_text", weights={"title": 3, "summary": 1})


def _record_run(summary: dict) -> None:
    from ..services.store import _db

    _db().harvest_runs.insert_one(dict(summary))


async def _tag_domains(opps: list[Opportunity], domains_by_id: dict[str, list[str]]) -> int:
    """Ask the local LLM which of our domains each program serves; adds to keyword tags."""
    from ..services import local_llm

    if await asyncio.to_thread(local_llm._init_backend) == "none":
        log.info("tagging skipped: no local LLM backend")
        return 0
    from ..models import StartupProfile

    n = 0
    for o in opps:
        if not o.summary:
            continue
        verdicts = await local_llm.judge(
            StartupProfile(description=f"a startup working in: {', '.join(DOMAINS)}"),
            [{"source_id": o.source_id, "title": o.title, "agency": o.agency,
              "summary": o.summary, "eligible_applicants": o.eligible_applicants}],
        )
        v = verdicts.get(o.source_id)
        if v and v.get("reason"):
            o.llm_reason = str(v["reason"])[:300]
            n += 1
    return n


def _count(opps: list[Opportunity], field: str) -> dict:
    out: dict = {}
    for o in opps:
        k = getattr(o, field) or "unknown"
        out[k] = out.get(k, 0) + 1
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--tag", action="store_true", help="also LLM-tag each program (slow)")
    ap.add_argument("--rows", type=int, default=40, help="rows per keyword search")
    args = ap.parse_args()
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    summary = asyncio.run(harvest(dry_run=args.dry_run, tag=args.tag, rows_each=args.rows))
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    sys.exit(main())
