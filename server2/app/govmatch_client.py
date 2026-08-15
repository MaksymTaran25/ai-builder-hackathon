"""Adapter: Server 2 -> Server 1 (GovMatch) GraphQL warehouse + matcher.

Server 1 owns the government data (MongoDB, nightly harvested, LLM-judged relevance).
Server 2 calls its GraphQL API and reshapes the result into Server 2's own response
contract, so Server 3 / the frontend see the same schema as before — now backed by
900+ live federal opportunities instead of 7 mocks.

Env: GOVMATCH_URL (default http://localhost:8000)
"""
from __future__ import annotations

import json
import os
import re
import urllib.request
from datetime import date, datetime
from typing import Any, Dict, List, Optional

from .models import (
    ActionStep,
    DetailedOverview,
    HistoricalAward,
    HistoricalIntelligence,
    RankedOpportunity,
    StartupQueryRequest,
    StrategyItem,
    SummaryMetrics,
    TimelineStep,
    OpportunityQueryResponse,
)

GOVMATCH_URL = os.environ.get("GOVMATCH_URL", "http://localhost:8000")

MATCH_PERSON_QUERY = "query M($p: JSON!) { match_person(person: $p) }"

FIT_LABEL = {
    "likely_fit": ("Likely Fit", "likely"),
    "potential_fit": ("Potential Fit — Verify Eligibility", "potential"),
    "adjacent": ("Adjacent Opportunity", "adjacent"),
    "not_a_fit": ("Probably Not a Fit", "unlikely"),
}


class GovMatchError(RuntimeError):
    pass


def _gql(query: str, variables: dict, timeout: int = 120) -> dict:
    req = urllib.request.Request(
        f"{GOVMATCH_URL}/graphql",
        json.dumps({"query": query, "variables": variables}).encode(),
        {"content-type": "application/json"},
    )
    try:
        resp = json.load(urllib.request.urlopen(req, timeout=timeout))
    except Exception as e:  # network / server down
        raise GovMatchError(f"GovMatch unreachable at {GOVMATCH_URL}: {e}") from e
    if resp.get("errors"):
        raise GovMatchError(f"GovMatch GraphQL error: {resp['errors'][0].get('message')}")
    return resp["data"]


def health() -> Dict[str, Any]:
    try:
        return json.load(urllib.request.urlopen(f"{GOVMATCH_URL}/api/health", timeout=3))
    except Exception as e:
        return {"ok": False, "error": str(e)}


# ---------------------------------------------------------------- formatting

def _usd(n: Optional[float]) -> str:
    if not n:
        return "—"
    if n >= 1_000_000:
        v = n / 1_000_000
        return f"${v:.0f}M" if v == int(v) else f"${v:.1f}M"
    if n >= 1_000:
        return f"${round(n / 1_000)}K"
    return f"${int(n)}"


def _value_text(o: dict) -> str:
    lo, hi = o.get("award_floor_usd"), o.get("award_ceiling_usd")
    if lo and hi:
        return f"{_usd(lo)}–{_usd(hi)}"
    if hi:
        return f"up to {_usd(hi)}"
    if o.get("source") == "sbir":
        return "$150K–$2M (Phase I/II)"
    return "See listing"


def _days_left(close: Optional[str]) -> int:
    if not close:
        return 365
    m = re.match(r"(\d{2})/(\d{2})/(\d{4})", close)
    if not m:
        return 365
    d = date(int(m.group(3)), int(m.group(1)), int(m.group(2)))
    return max((d - date.today()).days, 0)


def _deadline_text(close: Optional[str]) -> str:
    if not close:
        return "Rolling / see listing"
    m = re.match(r"(\d{2})/(\d{2})/(\d{4})", close)
    if not m:
        return close
    return date(int(m.group(3)), int(m.group(1)), int(m.group(2))).strftime("%B %-d, %Y")


def _short_agency(agency: str) -> str:
    table = {
        "National Institutes of Health": "NIH", "Department of Health and Human Services": "HHS",
        "U.S. National Science Foundation": "NSF", "National Science Foundation": "NSF",
        "Department of Defense": "DoD", "Department of War": "DoW", "Department of Energy": "DOE",
        "Environmental Protection Agency": "EPA", "Department of Homeland Security": "DHS",
        "National Aeronautics and Space Administration": "NASA", "Bureau of Reclamation": "USBR",
    }
    for k, v in table.items():
        if agency.startswith(k):
            return v
    words = [w for w in re.split(r"\s+", agency) if w[:1].isupper() and w.lower() not in ("of", "the", "and", "for")]
    return "".join(w[0] for w in words)[:6] or agency[:6]


def _category(o: dict) -> str:
    if o.get("source") == "sbir":
        return "R&D Grant (SBIR/STTR)"
    if o.get("source") == "utah":
        return "State Program"
    t = (o.get("title") or "").lower()
    if "sbir" in t or "sttr" in t:
        return "R&D Grant (SBIR/STTR)"
    if "procure" in t or "contract" in t or "baa" in t:
        return "Procurement / BAA"
    return "Federal Grant"


def _to_ranked(o: dict, state: Optional[str]) -> RankedOpportunity:
    label, code = FIT_LABEL.get(o.get("fit_tier"), ("Adjacent Opportunity", "adjacent"))
    ex = o.get("explanation") or {}
    hist = o.get("history") or {}
    days = _days_left(o.get("close_date"))
    agency = o.get("agency") or ""

    why_fit: List[str] = []
    if o.get("llm_reason"):
        why_fit.append(o["llm_reason"])
    if ex.get("why_fit"):
        why_fit.append(ex["why_fit"])
    if o.get("eligibility_flag") == "ok":
        why_fit.append("Official applicant types include small businesses")
    if hist.get("in_state_recipients"):
        why_fit.append(f"Demonstrated state precedent ({hist['in_state_recipients']} recipient(s) in {state or 'your state'})")

    concerns: List[str] = []
    if o.get("eligibility_flag") == "likely_ineligible":
        concerns.append("Listed applicant types do not include for-profit companies — partner or treat as intelligence")
    elif o.get("eligibility_flag") == "verify":
        concerns.append("Eligibility for small businesses not explicit — check 'Additional Information on Eligibility'")
    if o.get("cost_sharing"):
        concerns.append("Cost sharing required — you must contribute matching funds")
    if ex.get("concerns"):
        concerns.append(ex["concerns"])
    if 0 < days <= 30:
        concerns.append(f"Short deadline remaining ({days} days left)")

    samples = hist.get("sample_recipients") or []
    awards = [
        HistoricalAward(
            id=f"aw-{i+1}",
            company=str(r.get("name") or "Undisclosed"),
            program=str(r.get("program") or o.get("program") or ""),
            agency=str(r.get("agency") or _short_agency(agency)),
            amount=_usd(r.get("amount")),
            year=int(r.get("year") or 0),
            location=state or "",
            project_title=o.get("title") or "",
        )
        for i, r in enumerate(samples[:5])
    ]
    top_names = ", ".join(a.company for a in awards[:3]) or "See USAspending.gov"

    intel = HistoricalIntelligence(
        similar_companies_funded=int(hist.get("similar_companies") or 0),
        total_historical_awards=_usd(hist.get("total_awarded_usd")),
        median_award=_usd(hist.get("median_award_usd")),
        local_recipients=f"{hist.get('in_state_recipients') or 0} {state or 'in-state'} recipients",
        top_recipients_summary=top_names,
    )

    overview = DetailedOverview(
        why_should_i_care=ex.get("why_fit") or o.get("summary", "")[:400] or "Relevant federal program.",
        what_could_make_me_ineligible=[c for c in [ex.get("concerns")] if c] or ["Verify eligibility in the official listing"],
        what_should_i_verify=[c for c in [ex.get("verify")] if c] or ["Award size, deadline, applicant types"],
        what_should_i_do_next=[c for c in [ex.get("next_steps")] if c] or ["Register on SAM.gov; contact the program officer"],
        action_sequence=[
            ActionStep(step=1, title="Confirm eligibility", timeline="Week 1", detail=ex.get("verify") or "Read the official synopsis."),
            ActionStep(step=2, title="Registrations", timeline="Weeks 1–3", detail="SAM.gov UEI (free, ~2 weeks) and any agency portal."),
            ActionStep(step=3, title="Program officer contact", timeline="Weeks 2–4", detail="Email the listed contact with a one-paragraph fit summary."),
            ActionStep(step=4, title="Prepare & submit", timeline=f"before {_deadline_text(o.get('close_date'))}", detail=ex.get("next_steps") or "Assemble the application package."),
        ],
    )

    return RankedOpportunity(
        id=o.get("source_id") or "",
        title=o.get("title") or "",
        program_code=o.get("program") or "",
        agency=agency,
        agency_short=_short_agency(agency),
        category=_category(o),
        match_score=int(round(float(o.get("score") or 0))),
        fit_level=label,
        fit_level_code=code,
        potential_value=_value_text(o),
        deadline=_deadline_text(o.get("close_date")),
        days_left=days,
        closing_soon=days <= 90,
        summary=(o.get("summary") or "")[:600] or (o.get("title") or ""),
        why_fit=why_fit or ["Startup meets core federal program eligibility parameters"],
        concerns=concerns or ["Verify specific annual solicitation instructions"],
        historical_intelligence=intel,
        detailed_overview=overview,
        historical_awards=awards,
    )


# ---------------------------------------------------------------- strategy

def _strategy(ranked: List[RankedOpportunity]) -> List[StrategyItem]:
    tags = ["Highest Technical Alignment", "Strongest Funding Pool", "Best Secondary Path"]
    out = []
    for i, r in enumerate([x for x in ranked if x.fit_level_code in ("likely", "potential")][:3]):
        out.append(
            StrategyItem(
                rank=f"{i+1:02d}",
                opportunity_id=r.id,
                title=r.title[:80],
                agency=r.agency,
                potential_value=r.potential_value,
                rationale=r.why_fit[0] if r.why_fit else "Strong alignment with your profile.",
                tag=tags[i] if i < len(tags) else "Recommended",
            )
        )
    return out


def _timeline(ranked: List[RankedOpportunity]) -> List[TimelineStep]:
    today = date.today()
    months = []
    m = today.month
    for k in range(3):
        mm = (m - 1 + k) % 12 + 1
        months.append(date(today.year + (m - 1 + k) // 12, mm, 1).strftime("%B").upper())
    top = [r for r in ranked if r.fit_level_code in ("likely", "potential")][:3]
    soonest = sorted(top, key=lambda r: r.days_left)[:2]
    return [
        TimelineStep(
            month=months[0], phase="Phase 1: Readiness & Discovery",
            action="Confirm eligibility & entity registrations",
            deliverables=[
                "Confirm SAM.gov UEI is active (allow ~2 weeks if new)",
                *[f"Read full listing + email program officer: {r.title[:60]}" for r in top[:2]],
            ],
            status="current",
        ),
        TimelineStep(
            month=months[1], phase="Phase 2: Proposal Drafting & Letters of Support",
            action="Prepare materials for the strongest match",
            deliverables=[
                f"Draft technical narrative for {top[0].title[:60]}" if top else "Draft technical narrative",
                "Gather customer / partner letters of support",
                *[f"Watch deadline: {r.title[:50]} ({r.deadline})" for r in soonest],
            ],
            status="upcoming",
        ),
        TimelineStep(
            month=months[2], phase="Phase 3: Formal Submission",
            action="Submit strongest opportunity & queue the next",
            deliverables=[
                f"Submit {top[0].title[:60]}" if top else "Submit strongest application",
                f"Begin package for {top[1].title[:60]}" if len(top) > 1 else "Identify next-cycle opportunities",
            ],
            status="upcoming",
        ),
    ]


# ---------------------------------------------------------------- entrypoint

def query_govmatch(startup: StartupQueryRequest) -> OpportunityQueryResponse:
    """Full pipeline: Server 2 request -> Server 1 match_person -> Server 2 response."""
    person = {k: v for k, v in startup.model_dump().items() if v not in (None, "", {}, [])}
    # Give Server 1's mapper an explicit rich description: story + structured context,
    # so its extraction, embeddings and LLM judge all see the full picture.
    bits = [startup.story or ""]
    if startup.industry: bits.append(f"Industry: {startup.industry}.")
    if startup.technology: bits.append(f"Technology: {startup.technology}.")
    if startup.rd_activities: bits.append(f"R&D: {startup.rd_activities}.")
    if startup.target_customers: bits.append(f"Customers: {startup.target_customers}.")
    if startup.use_of_funds: bits.append(f"Use of funds: {startup.use_of_funds}.")
    person["description"] = " ".join(b for b in bits if b).strip() or startup.name or ""
    if startup.technology:
        person["technology"] = [t.strip() for t in re.split(r"[/,;]", startup.technology) if t.strip()]
    data = _gql(MATCH_PERSON_QUERY, {"p": person})["match_person"]

    state = (data.get("normalized_profile") or {}).get("state")
    ranked = [_to_ranked(o, state) for o in data.get("opportunities", [])]
    ranked.sort(key=lambda r: ({"likely": 3, "potential": 2, "adjacent": 1, "unlikely": 0}[r.fit_level_code], r.match_score), reverse=True)

    filters = startup.filters or {}
    if (mx := filters.get("max_deadline_days")) is not None:
        ranked = [r for r in ranked if r.days_left <= int(mx)]
    if (mn := filters.get("min_match_score")) is not None:
        ranked = [r for r in ranked if r.match_score >= int(mn)]

    s = data.get("summary") or {}
    total_val = s.get("total_potential_value_usd") or 0
    metrics = SummaryMetrics(
        total_opportunities=len(ranked),
        potential_funding_text=f"{_usd(total_val)}+" if total_val else "See listings",
        relevant_agencies=int(s.get("agencies") or len({r.agency for r in ranked})),
        closing_within_90_days=sum(1 for r in ranked if r.closing_soon),
    )

    return OpportunityQueryResponse(
        status="success",
        query_startup_name=startup.name or "Your Startup",
        total_opportunities=len(ranked),
        summary_metrics=metrics,
        ranked_opportunities=ranked,
        strategy_recommendations=_strategy(ranked),
        sequential_timeline=_timeline(ranked),
    )
