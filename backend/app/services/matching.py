"""Matching pipeline: query plan -> source fan-out -> score -> assemble response."""
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
from . import grants_gov, llm

log = logging.getLogger(__name__)

MAX_RETURNED = 12


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
    return Opportunity(
        source="grants_gov",
        source_id=f"gg-{hit.get('id')}",
        title=hit.get("title") or "",
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

    hits = await grants_gov.search_many(plan.keywords[:6], rows_each=20)
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
            o.score, o.fit_tier, _reason = scores[o.source_id]
    opps.sort(key=lambda o: o.score, reverse=True)
    opps = [o for o in opps if o.fit_tier != FitTier.not_fit][:MAX_RETURNED]

    # explanations for the ones we return (parallel)
    expl = await asyncio.gather(
        *(llm.explain(profile, {"title": o.title, "agency": o.agency, "program": o.program}) for o in opps),
        return_exceptions=True,
    )
    for o, e in zip(opps, expl):
        if not isinstance(e, Exception):
            o.explanation = e

    return MatchResponse(summary=_summarize(opps, overall_note), opportunities=opps)


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
