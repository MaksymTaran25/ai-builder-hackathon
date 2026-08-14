"""LLM seam: Claude when ANTHROPIC_API_KEY is set, deterministic mock otherwise.

Every public function degrades gracefully — an API failure falls back to the
mock path so the demo never depends on a key or the network being healthy.
"""
from __future__ import annotations

import logging
import os
import re
from typing import Optional

from pydantic import BaseModel, Field

from ..models import Explanation, FitTier, FollowUpQuestion, QueryPlan, StartupProfile
from . import vocab

log = logging.getLogger(__name__)

MODEL = os.environ.get("LLM_MODEL", "claude-opus-5")

_client = None


def provider() -> str:
    if os.environ.get("LLM_PROVIDER") == "mock":
        return "mock"
    if os.environ.get("ANTHROPIC_API_KEY"):
        return "anthropic"
    return "mock"


def _get_client():
    global _client
    if _client is None:
        from anthropic import AsyncAnthropic

        _client = AsyncAnthropic()
    return _client


# ---------------------------------------------------------------- extraction

CRITICAL_FIELDS = {
    "state": "Which state is your company based in?",
    "employees": "How many employees do you have?",
    "capital_need_max_usd": "Roughly how much funding are you looking for?",
    "industry": "What industry or market are you in?",
}


class _ExtractOut(BaseModel):
    profile: StartupProfile
    missing_critical: list[str] = Field(
        default_factory=list,
        description="Names of critical fields that genuinely could not be inferred from the text",
    )


async def extract_profile(text: str) -> tuple[StartupProfile, list[FollowUpQuestion]]:
    if provider() == "anthropic":
        try:
            return await _extract_claude(text)
        except Exception:
            log.exception("Claude extraction failed; using mock")
    return _extract_mock(text)


async def _extract_claude(text: str) -> tuple[StartupProfile, list[FollowUpQuestion]]:
    client = _get_client()
    resp = await client.messages.parse(
        model=MODEL,
        max_tokens=2000,
        output_config={"effort": "low"},
        system=(
            "You extract a structured startup profile from a founder's free-text description "
            "for a government-funding matching tool. Infer conservatively: only fill fields the "
            "text supports. Dollar fields are integers in USD (e.g. $1M ARR -> 1000000). "
            "state is the two-letter US state code. List a field in missing_critical only if it is "
            "one of: state, employees, capital_need_max_usd, industry — and truly absent."
        ),
        messages=[{"role": "user", "content": text}],
        output_format=_ExtractOut,
    )
    out: _ExtractOut = resp.parsed_output
    out.profile.description = text
    followups = [
        FollowUpQuestion(field=f, question=CRITICAL_FIELDS[f])
        for f in out.missing_critical
        if f in CRITICAL_FIELDS
    ]
    return out.profile, followups


_STATE_NAMES = {
    "utah": "UT", "california": "CA", "texas": "TX", "new york": "NY", "colorado": "CO",
    "idaho": "ID", "nevada": "NV", "arizona": "AZ", "washington": "WA", "oregon": "OR",
}


def _money(tok: str) -> int:
    tok = tok.replace(",", "").replace("$", "").strip().lower()
    mult = 1
    if tok.endswith("k"):
        mult, tok = 1_000, tok[:-1]
    elif tok.endswith("m"):
        mult, tok = 1_000_000, tok[:-1]
    elif tok.endswith("b"):
        mult, tok = 1_000_000_000, tok[:-1]
    try:
        return int(float(tok) * mult)
    except ValueError:
        return 0


def _extract_mock(text: str) -> tuple[StartupProfile, list[FollowUpQuestion]]:
    t = text.lower()
    p = StartupProfile(description=text)

    for name, code in _STATE_NAMES.items():
        if name in t:
            p.state = code
            break

    m = re.search(r"(\d+)[\s-]*(?:person|people|employees|employee)", t)
    if m:
        p.employees = int(m.group(1))

    m = re.search(r"raised\s+\$?([\d.,]+\s?[kmb]?)", t)
    if m:
        p.capital_raised_usd = _money(m.group(1))

    m = re.search(r"\$?([\d.,]+\s?[kmb]?)\s+(?:in\s+)?(?:arr|revenue)", t)
    if m:
        p.revenue_usd = _money(m.group(1))

    m = re.search(r"\$?([\d.,]+\s?[kmb]?)\s*[-–—to]+\s*\$?([\d.,]+\s?[kmb]?)\s*(?:of|in)?\s*(?:non-dilutive|funding|capital|need)?", t)
    if m and _money(m.group(1)) >= 1000:
        p.capital_need_min_usd = _money(m.group(1))
        p.capital_need_max_usd = _money(m.group(2))

    for kw, industry in [
        ("health", "Healthcare technology"), ("hospital", "Healthcare technology"),
        ("manufactur", "Advanced manufacturing"), ("aerospace", "Aerospace"),
        ("water", "Water technology"), ("cyber", "Cybersecurity"),
        ("education", "Consumer / education technology"), ("youth", "Consumer / education technology"),
    ]:
        if kw in t:
            p.industry = industry
            break

    tech = []
    for kw, label in [("ai", "AI"), ("machine learning", "Machine learning"), ("sensor", "Sensors"),
                      ("saas", "SaaS"), ("software", "Software"), ("platform", "Platform"),
                      ("marketplace", "Marketplace")]:
        if kw in t and label not in tech:
            tech.append(label)
    p.technology = tech

    followups = [
        FollowUpQuestion(field=f, question=q)
        for f, q in CRITICAL_FIELDS.items()
        if getattr(p, f, None) in (None, "", [])
    ]
    return p, followups


# ---------------------------------------------------------------- query plan

async def plan_queries(profile: StartupProfile) -> QueryPlan:
    base_kws, agencies, naics = vocab.translate(profile.description + " " + (profile.industry or ""))
    if provider() == "anthropic":
        try:
            return await _plan_claude(profile, base_kws, agencies, naics)
        except Exception:
            log.exception("Claude query planning failed; using mock")
    return QueryPlan(keywords=base_kws, agencies=agencies, naics=naics, research_topics=base_kws[:4])


async def _plan_claude(profile: StartupProfile, base_kws, agencies, naics) -> QueryPlan:
    client = _get_client()
    resp = await client.messages.parse(
        model=MODEL,
        max_tokens=1500,
        output_config={"effort": "low"},
        system=(
            "You translate a startup's profile into US federal-government funding vocabulary. "
            "Produce search keywords a grants database would actually contain (program language, "
            "not startup language), likely agency abbreviations, NAICS codes, and SBIR research "
            "topic phrases. 5-8 keywords max, most specific first. "
            f"Seed suggestions from a static table (improve on them): keywords={base_kws}, "
            f"agencies={agencies}, naics={naics}."
        ),
        messages=[{"role": "user", "content": profile.model_dump_json()}],
        output_format=QueryPlan,
    )
    plan: QueryPlan = resp.parsed_output
    # union with the deterministic table so the LLM can only add, not lose, coverage
    plan.keywords = list(dict.fromkeys(plan.keywords + base_kws))[:10]
    plan.agencies = list(dict.fromkeys(plan.agencies + agencies))[:8]
    plan.naics = list(dict.fromkeys(plan.naics + naics))[:8]
    return plan


# ---------------------------------------------------------------- scoring

class _ScoredItem(BaseModel):
    source_id: str
    score: float = Field(description="0-100 relevance of this opportunity to the startup")
    fit_tier: FitTier
    one_line_reason: str = ""


class _ScoreOut(BaseModel):
    items: list[_ScoredItem]
    overall_note: str = Field(
        default="",
        description="If federal fit is genuinely weak overall, say so honestly in 1-2 sentences; else empty",
    )


async def score_opportunities(
    profile: StartupProfile, candidates: list[dict]
) -> tuple[dict[str, tuple[float, FitTier, str]], str]:
    """candidates: [{source_id, title, agency, summary, keywords_matched}]
    Returns ({source_id: (score, tier, reason)}, overall_note)."""
    if provider() == "anthropic" and candidates:
        try:
            return await _score_claude(profile, candidates)
        except Exception:
            log.exception("Claude scoring failed; using mock")
    return _score_mock(candidates), ""


async def _score_claude(profile, candidates) -> tuple[dict[str, tuple[float, FitTier, str]], str]:
    client = _get_client()
    listing = "\n".join(
        f"- id={c['source_id']} | {c['title']} | agency={c.get('agency','')} | {c.get('summary','')[:200]}"
        for c in candidates
    )
    resp = await client.messages.parse(
        model=MODEL,
        max_tokens=8000,
        output_config={"effort": "medium"},
        system=(
            "You are a government funding analyst scoring opportunities for a startup. "
            "Score every candidate 0-100 and assign a fit tier: likely_fit (strong eligibility + "
            "topical match), potential_fit (plausible, eligibility must be verified), adjacent "
            "(related agency/theme but not this company's core), not_a_fit. Be honest: a weak "
            "match must NOT be inflated — judges reward saying 'there probably isn't a strong "
            "match'. Never present scores as eligibility determinations."
        ),
        messages=[{
            "role": "user",
            "content": f"STARTUP:\n{profile.model_dump_json()}\n\nCANDIDATES:\n{listing}",
        }],
        output_format=_ScoreOut,
    )
    out: _ScoreOut = resp.parsed_output
    return {i.source_id: (i.score, i.fit_tier, i.one_line_reason) for i in out.items}, out.overall_note


def _score_mock(candidates) -> dict[str, tuple[float, FitTier, str]]:
    scored = {}
    for c in candidates:
        n_kw = len(c.get("keywords_matched") or [])
        score = min(95.0, 35.0 + 18.0 * n_kw)
        if score >= 70:
            tier = FitTier.likely
        elif score >= 55:
            tier = FitTier.potential
        elif score >= 40:
            tier = FitTier.adjacent
        else:
            tier = FitTier.not_fit
        reason = f"Matched {n_kw} of your search themes" if n_kw else "Weak topical overlap"
        scored[c["source_id"]] = (score, tier, reason)
    return scored


# ---------------------------------------------------------------- explanations

async def explain(profile: StartupProfile, opp: dict) -> Explanation:
    if provider() == "anthropic":
        try:
            return await _explain_claude(profile, opp)
        except Exception:
            log.exception("Claude explanation failed; using mock")
    return _explain_mock(profile, opp)


async def _explain_claude(profile: StartupProfile, opp: dict) -> Explanation:
    client = _get_client()
    resp = await client.messages.parse(
        model=MODEL,
        max_tokens=2000,
        output_config={"effort": "low"},
        system=(
            "Explain a government funding opportunity to a startup founder in plain language, "
            "no jargon. Four short sections (2-3 sentences each): why_fit (why this looks "
            "relevant), concerns (what could make them ineligible), verify (what to confirm in "
            "the official listing), next_steps (concrete actions incl. registrations like "
            "SAM.gov). Never present this as a definitive eligibility determination."
        ),
        messages=[{
            "role": "user",
            "content": f"STARTUP:\n{profile.model_dump_json()}\n\nOPPORTUNITY:\n{opp}",
        }],
        output_format=Explanation,
    )
    return resp.parsed_output


def _explain_mock(profile: StartupProfile, opp: dict) -> Explanation:
    ind = profile.industry or "your sector"
    return Explanation(
        why_fit=(
            f"{opp.get('title', 'This program')} ({opp.get('agency', 'federal agency')}) funds work "
            f"aligned with {ind}. Your profile matches its topical focus."
        ),
        concerns=(
            "Eligibility rules (small-business size standards, US ownership, prior awards) and "
            "cost-sharing requirements may exclude some applicants."
        ),
        verify=(
            "Read the official synopsis for eligibility categories, deadlines, and award size; "
            "confirm your size standard and registration status."
        ),
        next_steps=(
            "Register on SAM.gov (free, takes ~2 weeks), get a UEI, review the full announcement, "
            "and contact the listed program officer before applying."
        ),
    )
