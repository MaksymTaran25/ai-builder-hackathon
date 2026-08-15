"""Matching pipeline: plan -> fan-out -> prefilter -> enrich -> score -> assemble."""
from __future__ import annotations

import asyncio
import html
import logging
import re
from datetime import date, datetime

from ..models import (
    AgencyMapEntry,
    FitTier,
    MatchResponse,
    MatchSummary,
    Opportunity,
    SimilarCompany,
    StartupProfile,
)
from . import eligibility, grants_gov, llm, local_llm, sbir, store, usaspending, utah

log = logging.getLogger(__name__)

PREFILTER_N = 24   # candidates that get full details fetched
LLM_JUDGE_N = 14   # top candidates the local LLM reads in full
MAX_RETURNED = 10
HISTORY_TOP_N = 8  # opportunities that get USAspending history

_TIER_ORDER = [FitTier.not_fit, FitTier.adjacent, FitTier.potential, FitTier.likely]


def _reconcile_tier(embedding_tier: FitTier, llm_tier: FitTier) -> FitTier:
    """LLM verdict vs embedding tier: outright not_a_fit is a veto; otherwise the LLM
    may move the tier by at most one step in either direction (a 4B model's opinion
    should refine the ranking, not replace it)."""
    if llm_tier == FitTier.not_fit:
        return llm_tier
    e, l = _TIER_ORDER.index(embedding_tier), _TIER_ORDER.index(llm_tier)
    if l < e:
        return _TIER_ORDER[max(e - 1, l)]
    return _TIER_ORDER[min(e + 1, l)]


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
        title=html.unescape(hit.get("title") or ""),
        agency=hit.get("agency") or hit.get("agencyCode") or "",
        agency_code=hit.get("agencyCode") or "",
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
    rd = _has_rd_signal(profile)

    hits, sbir_opps, similar_rows = await asyncio.gather(
        grants_gov.search_many(plan.keywords[:6], rows_each=20),
        asyncio.to_thread(sbir.pathway_opportunities, topics, profile.state),
        asyncio.to_thread(sbir.similar_awards, topics, profile.state, 400),
    )

    opps = [_grants_hit_to_opp(h) for h in hits]
    kw_by_id = {f"gg-{h.get('id')}": h.get("_matched_keywords", []) for h in hits}

    # Stage A: cheap title-level semantic prefilter so we only fetch details for plausible ones
    opps = await asyncio.to_thread(_prefilter, profile, opps, kw_by_id)

    # Stage B: full details for the survivors — synopsis, award data, applicant types
    await _attach_details(opps)
    # warehouse: persist everything we fetched, queryable by any other process
    await asyncio.to_thread(store.upsert_opportunities, opps)

    # Stage C: score with real program text
    candidates = [
        {
            "source_id": o.source_id,
            "title": o.title,
            "agency": o.agency,
            "summary": o.summary[:500],
            "keywords_matched": kw_by_id.get(o.source_id, []),
        }
        for o in opps
    ]
    scores, overall_note = await llm.score_opportunities(profile, candidates)
    for o in opps:
        if o.source_id in scores:
            o.score, o.fit_tier, _ = scores[o.source_id]

    # Stage C2: local LLM (MLX, offline) reads each synopsis and judges real relevance.
    # Blend: 55% LLM verdict, 45% embedding score. Tier: the LLM can demote by one
    # notch, veto outright with not_a_fit, and promote by at most one; the parsed
    # applicant-type code (authoritative) overrides its "can't apply" guess.
    opps.sort(key=lambda o: o.score, reverse=True)
    judged_set = opps[:LLM_JUDGE_N]
    verdicts = await local_llm.judge(
        profile,
        [
            {
                "source_id": o.source_id, "title": o.title, "agency": o.agency,
                "summary": o.summary, "eligible_applicants": o.eligible_applicants,
            }
            for o in judged_set
        ],
    )
    for o in judged_set:
        v = verdicts.get(o.source_id)
        if not v:
            continue
        o.llm_reason = str(v.get("reason") or "")[:300]
        rel = float(v.get("relevance") or 0)
        o.score = round(0.55 * rel + 0.45 * o.score, 1)
        llm_tier = FitTier(v.get("fit_tier")) if v.get("fit_tier") in FitTier._value2member_map_ else None
        if llm_tier is not None:
            o.fit_tier = _reconcile_tier(o.fit_tier, llm_tier)
        # "can't apply" from the model only counts when the official applicant list agrees
        if (
            not v.get("startup_can_apply", True)
            and o.eligibility_flag != "ok"
            and o.fit_tier == FitTier.likely
        ):
            o.fit_tier = FitTier.potential

    # Stage D: eligibility gate — a program that can't fund a for-profit startup is
    # adjacent intelligence, not a recommendation
    profile_text = " ".join(
        filter(None, [profile.description, profile.industry, " ".join(profile.technology or [])])
    ).lower()
    for o in opps:
        if o.eligibility_flag == "likely_ineligible" and o.fit_tier in (FitTier.likely, FitTier.potential):
            o.fit_tier = FitTier.adjacent
            o.score = min(o.score, 52.0)
        elif _is_foreign_affairs(o) and o.fit_tier in (FitTier.likely, FitTier.potential):
            # embassy/public-diplomacy grants fund programming abroad, not US startup R&D,
            # however topical their titles sound
            o.fit_tier = FitTier.adjacent
            o.score = min(o.score, 50.0)
        elif _sector_mismatch(o, profile_text) and o.fit_tier == FitTier.likely:
            # related technology but a different customer sector: one notch down
            o.fit_tier = FitTier.potential
            o.score -= 15.0

    # SBIR pathway cards: deterministic score from award history depth
    for o in sbir_opps:
        n = o.history.similar_companies if o.history else 0
        o.score = min(92.0, 68.0 + n / 8)
        o.fit_tier = FitTier.likely if n >= 40 else FitTier.potential if n >= 8 else FitTier.adjacent
        o.eligibility_flag = "ok" if rd else "verify"
        if not rd:
            # SBIR funds R&D; a non-R&D business model can't be a likely fit
            o.score = min(o.score, 48.0)
            o.fit_tier = FitTier.adjacent

    opps = [o for o in opps if o.fit_tier != FitTier.not_fit]
    tier_rank = {FitTier.likely: 3, FitTier.potential: 2, FitTier.adjacent: 1, FitTier.not_fit: 0}
    merged = sorted(
        sbir_opps + opps, key=lambda o: (tier_rank[o.fit_tier], o.score), reverse=True
    )[:MAX_RETURNED]

    # An SBIR pathway with deep award history belongs on the map even when posted
    # grants edge it out on score — it's the canonical non-dilutive route.
    best_sbir = max(sbir_opps, key=lambda o: o.score, default=None)
    if (
        best_sbir
        and best_sbir not in merged
        and rd
        and best_sbir.history
        and best_sbir.history.similar_companies >= 8
    ):
        merged = merged[: MAX_RETURNED - 1] + [best_sbir]
        merged.sort(key=lambda o: o.score, reverse=True)

    if not rd:
        for o in merged:
            if o.fit_tier == FitTier.likely:
                o.fit_tier = FitTier.potential
                o.score = min(o.score, 67.0)

    top5 = sorted((o.score for o in merged), reverse=True)[:5]
    weak_overall = (
        not rd
        or len([o for o in merged if o.fit_tier in (FitTier.likely, FitTier.potential)]) <= 2
        or (top5 and sorted(top5)[len(top5) // 2] < 70)
    )
    if not overall_note and weak_overall:
        overall_note = (
            "Traditional federal grants look like a weak fit for this business model — most "
            "programs below are adjacent at best. Consider state/local economic development "
            "programs, SBA lending (7(a)/microloans), and government customers rather than "
            "grant funding as the primary path."
        )

    if profile.state == "UT":
        merged.extend(utah.match_programs(profile.description, profile.industry, max_n=3))

    # Stage E: history for the top federal cards + explanations for everything
    await _attach_history(merged[:HISTORY_TOP_N], profile)
    expl = await asyncio.gather(
        *(
            llm.explain(
                profile,
                {
                    "title": o.title, "agency": o.agency, "program": o.program,
                    "summary": o.summary[:600], "close_date": o.close_date,
                    "award_range": [o.award_floor_usd, o.award_ceiling_usd],
                    "cost_sharing": o.cost_sharing,
                    "eligibility_flag": o.eligibility_flag,
                    "eligible_applicants": o.eligible_applicants,
                },
            )
            for o in merged
        ),
        return_exceptions=True,
    )
    for o, e in zip(merged, expl):
        if not isinstance(e, Exception):
            o.explanation = e

    result = MatchResponse(
        summary=_summarize(merged, overall_note),
        opportunities=merged,
        similar_companies=_similar_companies(similar_rows, profile.state),
        agency_map=_agency_map(merged, similar_rows),
    )
    await asyncio.to_thread(store.save_match_run, profile, result)
    return result


# ------------------------------------------------------------------ stages

def _prefilter(profile: StartupProfile, opps: list[Opportunity], kw_by_id) -> list[Opportunity]:
    if len(opps) <= PREFILTER_N:
        return opps
    from . import embeddings

    query = " ".join(
        filter(None, [profile.description, profile.industry, " ".join(profile.technology or [])])
    )
    try:
        sims = embeddings.similarities(query, [f"{o.title} — {o.agency}" for o in opps])
    except Exception:
        log.exception("prefilter embeddings failed; keeping first N")
        return opps[:PREFILTER_N]
    ranked = sorted(
        zip(opps, sims),
        key=lambda p: float(p[1]) + 0.02 * len(kw_by_id.get(p[0].source_id, [])),
        reverse=True,
    )
    return [o for o, _ in ranked[:PREFILTER_N]]


async def _attach_details(opps: list[Opportunity]) -> None:
    ids = [o.source_id.removeprefix("gg-") for o in opps if o.source == "grants_gov"]
    details = await grants_gov.fetch_details_many(ids)
    for o in opps:
        d = details.get(o.source_id.removeprefix("gg-"))
        if not d:
            continue
        syn = d.get("synopsis") or {}
        o.award_floor_usd = _num(syn.get("awardFloor"))
        o.award_ceiling_usd = _num(syn.get("awardCeiling"))
        o.estimated_total_funding_usd = _num(syn.get("estimatedFunding"))
        o.expected_awards = int(_num(syn.get("numberOfAwards")) or 0) or None
        o.cost_sharing = syn.get("costSharing") in (True, "true", "Yes", "yes")
        o.summary = _strip_html(syn.get("synopsisDesc") or "")[:900]
        if syn.get("responseDateStr"):
            # fetchOpportunity format: "2026-08-20-00-00-00" -> "08/20/2026"
            m = re.match(r"(\d{4})-(\d{2})-(\d{2})", syn["responseDateStr"])
            if m:
                o.close_date = f"{m.group(2)}/{m.group(3)}/{m.group(1)}"
        flag, descs = eligibility.evaluate(syn.get("applicantTypes") or [])
        o.eligibility_flag = flag
        o.eligible_applicants = descs[:6]


async def _attach_history(opps: list[Opportunity], profile: StartupProfile) -> None:
    async def one(o: Opportunity) -> None:
        if o.source == "grants_gov" and o.cfda:
            o.history = await usaspending.awards_for_cfda(o.cfda, profile.state)
            if o.history:
                await asyncio.to_thread(store.save_history, o.cfda, profile.state, o.history)

    await asyncio.gather(*(one(o) for o in opps))


# ------------------------------------------------------------------ intelligence

def _similar_companies(rows, state) -> list[SimilarCompany]:
    by_co: dict[str, dict] = {}
    for r in rows:
        c = by_co.setdefault(
            r["company"],
            {"state": r["state"], "agency": {}, "total": 0.0, "n": 0, "year": 0, "title": r["title"], "program": f"{r['program']}"},
        )
        c["total"] += r["award_amount"] or 0
        c["n"] += 1
        c["year"] = max(c["year"], r["award_year"] or 0)
        c["agency"][r["agency"]] = c["agency"].get(r["agency"], 0) + 1
    ranked = sorted(
        by_co.items(),
        key=lambda kv: (kv[1]["state"] == state, kv[1]["total"]),
        reverse=True,
    )
    out = []
    for name, c in ranked[:8]:
        top_agency = max(c["agency"], key=c["agency"].get) if c["agency"] else ""
        out.append(
            SimilarCompany(
                name=(name or "").title(),
                state=c["state"] or "",
                agency=sbir._short_agency(top_agency),
                program=c["program"],
                total_usd=c["total"],
                awards=c["n"],
                latest_year=c["year"] or None,
                example_title=c["title"][:90],
            )
        )
    return out


def _agency_map(opps: list[Opportunity], sbir_rows) -> list[AgencyMapEntry]:
    entries: dict[str, AgencyMapEntry] = {}
    for o in opps:
        if o.source not in ("grants_gov", "sbir") or not o.agency:
            continue
        e = entries.setdefault(
            o.agency, AgencyMapEntry(agency=o.agency, short=sbir._short_agency(o.agency))
        )
        e.open_opportunities += 1
        if not e.note and o.fit_tier == FitTier.likely:
            e.note = f"e.g. {o.title[:70]}"
    for r in sbir_rows:
        if r["agency"] in entries:
            entries[r["agency"]].similar_awards_since_2018 += 1
        else:
            e = entries.setdefault(
                r["agency"],
                AgencyMapEntry(agency=r["agency"], short=sbir._short_agency(r["agency"])),
            )
            e.similar_awards_since_2018 += 1
    ranked = sorted(
        entries.values(),
        key=lambda e: (e.open_opportunities, e.similar_awards_since_2018),
        reverse=True,
    )
    return [e for e in ranked if e.open_opportunities or e.similar_awards_since_2018 >= 3][:6]


# ------------------------------------------------------------------ shared helpers

FOREIGN_AFFAIRS_MARKERS = (
    "embassy", "consulate", "u.s. mission", "public diplomacy", "american spaces",
    "department of state", "agency for international development",
)


def _is_foreign_affairs(o: Opportunity) -> bool:
    blob = f"{o.agency} {o.title} {o.summary[:300]}".lower()
    return (
        any(m in blob for m in FOREIGN_AFFAIRS_MARKERS)
        or o.agency_code.upper().startswith(("DOS", "USAID"))
    )


OIL_GAS_MARKERS = ("oil and gas", "petroleum", "fossil energy", "oilfield", "produced water")


def _sector_mismatch(o: Opportunity, profile_text: str) -> bool:
    """Candidate is an oil & gas program but the company never mentions that sector."""
    cand = f"{o.title} {o.summary[:300]}".lower()
    return any(m in cand for m in OIL_GAS_MARKERS) and not any(
        m in profile_text for m in OIL_GAS_MARKERS + ("oil", "gas", "energy")
    )


RD_TERMS = (
    "r&d", "research", "develop", "ai", "machine learning", "sensor", "hardware",
    "clinical", "biotech", "manufactur", "cyber", "engineering", "prototype",
    "patent", "deep tech", "platform",
)
CONSUMER_TERMS = ("marketplace", "parents", "consumer", "enrichment", "booking", "e-commerce")


def _has_rd_signal(profile: StartupProfile) -> bool:
    """SBIR/most federal grants fund R&D. Consumer businesses without R&D language
    should be told the truth instead of shown inflated matches."""
    text = " ".join(
        filter(None, [profile.description, profile.industry, " ".join(profile.technology or [])])
    ).lower()
    consumer = any(w in text for w in CONSUMER_TERMS)
    rd_hits = sum(1 for w in RD_TERMS if re.search(rf"\b{re.escape(w)}", text))
    if consumer:
        return rd_hits >= 3  # a consumer marketplace needs real R&D language to count
    return rd_hits >= 1


def _num(v):
    try:
        f = float(str(v).replace(",", ""))
        return f if f > 0 else None
    except (TypeError, ValueError):
        return None


def _strip_html(s: str) -> str:
    return html.unescape(re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", s)).strip())


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
