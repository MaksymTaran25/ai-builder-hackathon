"""Curated Utah state programs — the optional 'Utah advantage' layer.

Small hand-checked dataset; matched by domain tags + embedding similarity.
These complement federal results and become the constructive recommendation
when federal fit is weak. Details should be verified on the linked sites.
"""
from __future__ import annotations

from typing import Optional

from ..models import Explanation, FitTier, Opportunity

UTAH_PROGRAMS: list[dict] = [
    {
        "id": "utah-innovation-fund",
        "title": "Utah Innovation Fund — pre-seed capital for Utah startups",
        "org": "Utah Innovation Fund (state-backed)",
        "type": "Equity investment (state-backed pre-seed)",
        "tags": ["all", "rd", "software", "hardware"],
        "summary": "State-backed pre-seed fund investing in early Utah technology companies, created by the Utah legislature to back university-affiliated and homegrown startups.",
        "url": "https://utahinnovationfund.com/",
    },
    {
        "id": "utah-ssbci",
        "title": "Utah SSBCI — state loan & equity programs for small business",
        "org": "Governor's Office of Economic Opportunity (GOEO)",
        "type": "Loan participation / equity (federal-state SSBCI)",
        "tags": ["all"],
        "summary": "Utah administers federal State Small Business Credit Initiative capital through loan participation and venture programs for Utah small businesses that struggle to access conventional financing.",
        "url": "https://business.utah.gov/",
    },
    {
        "id": "utah-edtif",
        "title": "EDTIF — post-performance tax credit for expansion in Utah",
        "org": "Governor's Office of Economic Opportunity (GOEO)",
        "type": "Post-performance tax credit",
        "tags": ["all", "manufacturing", "expansion"],
        "summary": "Refundable tax credit of up to ~30% of new state revenues over the project life for companies creating high-paying jobs in Utah — relevant when you scale headcount or facilities.",
        "url": "https://business.utah.gov/edtif/",
    },
    {
        "id": "utah-step",
        "title": "STEP export grant — international sales support",
        "org": "World Trade Center Utah / SBA",
        "type": "Grant (export development)",
        "tags": ["all", "export"],
        "summary": "SBA State Trade Expansion Program funds administered in Utah for small businesses starting or growing exports — trade shows, international marketing, compliance costs.",
        "url": "https://wtcutah.com/",
    },
    {
        "id": "utah-custom-fit",
        "title": "Custom Fit — employee training reimbursement",
        "org": "Utah System of Higher Education / technical colleges",
        "type": "Training funds (reimbursement)",
        "tags": ["all", "workforce", "manufacturing"],
        "summary": "State training dollars delivered through Utah technical colleges that reimburse part of the cost of training your Utah employees — useful while scaling a technical team.",
        "url": "https://utahworks.utah.edu/",
    },
    {
        "id": "utah-impact",
        "title": "iMpact Utah / Manufacturing Extension Partnership",
        "org": "iMpact Utah (NIST MEP affiliate)",
        "type": "Subsidized consulting (manufacturing)",
        "tags": ["manufacturing"],
        "summary": "Utah's NIST Manufacturing Extension Partnership affiliate: subsidized operational, quality, and scale-up consulting for Utah manufacturers.",
        "url": "https://impactutah.org/",
    },
    {
        "id": "utah-rural",
        "title": "Rural Economic Development Incentive (REDI)",
        "org": "Governor's Office of Economic Opportunity (GOEO)",
        "type": "Grant (per-job, rural)",
        "tags": ["rural", "all"],
        "summary": "Per-new-position grants for companies creating remote or on-site jobs in rural Utah counties.",
        "url": "https://business.utah.gov/rural/",
    },
]


def match_programs(profile_text: str, industry: Optional[str], max_n: int = 3) -> list[Opportunity]:
    """Pick the most relevant Utah programs for this profile."""
    text = f"{profile_text} {industry or ''}".lower()
    picks: list[dict] = []

    def add(p):
        if p not in picks:
            picks.append(p)

    if any(w in text for w in ("manufactur", "hardware", "aerospace", "component")):
        add(_by_id("utah-impact"))
        add(_by_id("utah-custom-fit"))
        add(_by_id("utah-edtif"))
    if any(w in text for w in ("software", "ai", "platform", "saas", "sensor", "cyber", "marketplace", "app")):
        add(_by_id("utah-innovation-fund"))
        add(_by_id("utah-ssbci"))
    if "export" in text or "international" in text:
        add(_by_id("utah-step"))
    add(_by_id("utah-ssbci"))
    add(_by_id("utah-innovation-fund"))

    out = []
    for p in picks[:max_n]:
        out.append(
            Opportunity(
                source="utah",
                source_id=p["id"],
                title=p["title"],
                agency=p["org"],
                program=p["type"],
                status="state program",
                url=p["url"],
                summary=p["summary"],
                score=62.0,
                fit_tier=FitTier.potential,
                explanation=Explanation(
                    why_fit=f"{p['summary']} As a Utah company you're in its target population.",
                    concerns="State programs have their own size, industry, and job-creation criteria; some are competitive or first-come.",
                    verify="Confirm current eligibility, funding availability, and application windows on the program site.",
                    next_steps=f"Contact the administering organization ({p['org']}) — Utah's programs are relationship-driven and staff respond quickly.",
                ),
            )
        )
    return out


def _by_id(pid: str) -> dict:
    return next(p for p in UTAH_PROGRAMS if p["id"] == pid)
