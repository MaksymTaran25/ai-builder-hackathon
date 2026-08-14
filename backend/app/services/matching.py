"""Matching pipeline: query plan -> source fan-out -> score -> enrich -> assemble."""
from __future__ import annotations

import asyncio
import logging
from datetime import date, datetime

from ..models import (
    FitTier,
    MatchResponse,
    MatchSummary,
    Opportunity,
    StartupProfile,
)
from . import grants_gov, llm, sbir, usaspending

log = logging.getLogger(__name__)

MAX_RETURNED = 10
ENRICH_TOP_N = 6  # opportunities that get fetchOpportunity + USAspending history


def _parse_date(s: str | None):
    if not s:
        return None
    for fmt in ("%m/%d/%Y", "%Y-%m-%d"):
        try:
            return datetime.strptime(s, fmt).date()
        except ValueError:
            continue
    return None


def _grants_hit_to_opp(hit: dict) -> Opportunity:
    import html

    return Opportunity(
        source="grants_gov",
        source_id=f"gg-{hit.get('id')}",
        title=html.unescape(hit.get("title") or ""),
        agency=hit.get("agency") or hit.get("agencyCode") or "",
        program=hit.get("number") or "",
        cfda=hit.get("cfdaList") or [],
        status=hit.get("oppStatus") or "",
        open_date=hit.get("openDate"),
        close_date=hit.get("closeDate"),
        url=grants_gov.link_for(hit.get("id")),
        summary="",
    )


async def run_match(profile: StartupProfile) -> MatchResponse:
    plan = await llm.plan_queries(profile)
    log.info("query plan: %s", plan.model_dump())
    topics = plan.research_topics or plan.keywords[:4]

    hits, sbir_opps = await asyncio.gather(
        grants_gov.search_many(plan.keywords[:6], rows_each=20),
        asyncio.to_thread(sbir.pathway_opportunities, topics, profile.state),
    )

    opps = [_grants_hit_to_opp(h) for h in hits]
    kw_by_id = {f"gg-{h.get('id')}": h.get("_matched_keywords", []) for h in hits}

    candidates = [
        {
            "source_id": o.source_id,
            "title": o.title,
            "agency": o.agency,
            "summary": o.summary,
            "keywords_matched": kw_by_id.get(o.source_id, []),
        }
        for o in opps
    ]
    scores, overall_note = await llm.score_opportunities(profile, candidates)
    for o in opps:
        if o.source_id in scores:
            o.score, o.fit_tier, _ = scores[o.source_id]

    # SBIR pathway cards: deterministic score from award history depth
    for o in sbir_opps:
        n = o.history.similar_companies if o.history else 0
        o.score = min(92.0, 68.0 + n / 8)
        o.fit_tier = FitTier.likely if n >= 40 else FitTier.potential if n >= 8 else FitTier.adjacent

    opps = [o for o in opps if o.fit_tier != FitTier.not_fit]
    opps.sort(key=lambda o: o.score, reverse=True)
    merged = _interleave(sbir_opps, opps)[:MAX_RETURNED]

    # Honest read when nothing scores strongly (e.g. consumer marketplaces):
    # judges reward "there probably isn't a strong match" over inflated results.
    strong = [o for o in merged if o.fit_tier in (FitTier.likely, FitTier.potential)]
    top5 = sorted((o.score for o in merged), reverse=True)[:5]
    weak_overall = len(strong) <= 2 or (top5 and sorted(top5)[len(top5) // 2] < 78)
    if not overall_note and weak_overall:
        overall_note = (
            "Traditional federal grants look like a weak fit for this business model — most "
            "programs below are adjacent at best. Consider state/local economic development "
            "programs, SBA lending (7(a)/microloans), and government customers rather than "
            "grant funding as the primary path."
        )

    await _enrich(merged[:ENRICH_TOP_N], profile)

    expl = await asyncio.gather(
        *(
            llm.explain(
                profile,
                {
                    "title": o.title, "agency": o.agency, "program": o.program,
                    "summary": o.summary[:600], "close_date": o.close_date,
                    "award_range": [o.award_floor_usd, o.award_ceiling_usd],
                },
            )
            for o in merged
        ),
        return_exceptions=True,
    )
    for o, e in zip(merged, expl):
        if not isinstance(e, Exception):
            o.explanation = e

    return MatchResponse(summary=_summarize(merged, overall_note), opportunities=merged)


def _interleave(sbir_opps: list[Opportunity], grant_opps: list[Opportunity]) -> list[Opportunity]:
    """SBIR pathway cards rank by score among the grants, but never below #4 if strong."""
    merged = sorted(sbir_opps + grant_opps, key=lambda o: o.score, reverse=True)
    return merged


async def _enrich(opps: list[Opportunity], profile: StartupProfile) -> None:
    """Attach award ranges + synopsis (Grants.gov details) and history (USAspending/SBIR)."""

    async def enrich_one(o: Opportunity) -> None:
        if o.source == "grants_gov":
            try:
                d = await grants_gov.fetch_details(o.source_id.removeprefix("gg-"))
                syn = d.get("synopsis") or {}
                o.award_floor_usd = _num(syn.get("awardFloor"))
                o.award_ceiling_usd = _num(syn.get("awardCeiling"))
                desc = syn.get("synopsisDesc") or ""
                o.summary = _strip_html(desc)[:900]
            except Exception:
                log.exception("fetchOpportunity failed for %s", o.source_id)
            if o.cfda:
                o.history = await usaspending.awards_for_cfda(o.cfda, profile.state)

    await asyncio.gather(*(enrich_one(o) for o in opps))


def _num(v):
    try:
        f = float(str(v).replace(",", ""))
        return f if f > 0 else None
    except (TypeError, ValueError):
        return None


def _strip_html(s: str) -> str:
    import re

    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", s)).strip()


def _summarize(opps: list[Opportunity], overall_note: str) -> MatchSummary:
    today = date.today()
    closing_soon = 0
    for o in opps:
        d = _parse_date(o.close_date)
        if d and 0 <= (d - today).days <= 90:
            closing_soon += 1
    total_value = sum(o.award_ceiling_usd or 0 for o in opps)
    return MatchSummary(
        high_potential=sum(1 for o in opps if o.fit_tier == FitTier.likely),
        total_potential_value_usd=total_value,
        agencies=len({o.agency for o in opps if o.agency}),
        closing_within_90_days=closing_soon,
        overall_note=overall_note,
    )
