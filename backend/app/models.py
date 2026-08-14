"""Pydantic schemas shared across the API."""
from __future__ import annotations

from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class StartupProfile(BaseModel):
    """Structured company profile extracted from the founder's description."""

    description: str = ""
    industry: Optional[str] = None
    technology: list[str] = Field(default_factory=list)
    city: Optional[str] = None
    state: Optional[str] = None  # two-letter code, e.g. "UT"
    employees: Optional[int] = None
    revenue_usd: Optional[int] = None
    capital_raised_usd: Optional[int] = None
    funding_stage: Optional[str] = None
    rd_activities: Optional[str] = None
    product_maturity: Optional[str] = None
    target_customers: Optional[str] = None
    capital_need_min_usd: Optional[int] = None
    capital_need_max_usd: Optional[int] = None
    use_of_funds: Optional[str] = None


class FollowUpQuestion(BaseModel):
    field: str
    question: str


class ExtractResponse(BaseModel):
    profile: StartupProfile
    followups: list[FollowUpQuestion] = Field(default_factory=list)


class QueryPlan(BaseModel):
    """Startup language translated into government-search vocabulary."""

    keywords: list[str] = Field(default_factory=list)  # for Grants.gov / USAspending
    agencies: list[str] = Field(default_factory=list)  # agency codes like HHS, NSF, DOD
    naics: list[str] = Field(default_factory=list)
    research_topics: list[str] = Field(default_factory=list)  # for SBIR corpus retrieval


class FitTier(str, Enum):
    likely = "likely_fit"
    potential = "potential_fit"
    adjacent = "adjacent"
    not_fit = "not_a_fit"


class Explanation(BaseModel):
    why_fit: str = ""
    concerns: str = ""
    verify: str = ""
    next_steps: str = ""


class HistoricalStats(BaseModel):
    similar_companies: int = 0
    total_awarded_usd: float = 0
    median_award_usd: float = 0
    in_state_recipients: int = 0
    sample_recipients: list[dict] = Field(default_factory=list)  # name, program, agency, amount, year


class Opportunity(BaseModel):
    source: str  # grants_gov | sbir | assistance_listing | usaspending | utah
    source_id: str
    title: str
    agency: str = ""
    program: str = ""
    status: str = ""  # posted | forecasted | open solicitation ...
    cfda: list[str] = Field(default_factory=list)  # ALN numbers -> USAspending join key
    open_date: Optional[str] = None
    close_date: Optional[str] = None
    award_floor_usd: Optional[float] = None
    award_ceiling_usd: Optional[float] = None
    estimated_total_funding_usd: Optional[float] = None
    expected_awards: Optional[int] = None
    cost_sharing: Optional[bool] = None
    eligibility_flag: Optional[str] = None  # ok | verify | likely_ineligible
    eligible_applicants: list[str] = Field(default_factory=list)
    url: Optional[str] = None
    summary: str = ""
    score: float = 0  # 0-100 relevance
    fit_tier: FitTier = FitTier.adjacent
    explanation: Optional[Explanation] = None
    history: Optional[HistoricalStats] = None


class MatchSummary(BaseModel):
    high_potential: int = 0
    total_potential_value_usd: float = 0
    agencies: int = 0
    closing_within_90_days: int = 0
    overall_note: str = ""  # honest "weak federal fit" note for e.g. test case 5


class SimilarCompany(BaseModel):
    name: str
    state: str = ""
    agency: str = ""
    program: str = ""
    total_usd: float = 0
    awards: int = 0
    latest_year: Optional[int] = None
    example_title: str = ""


class AgencyMapEntry(BaseModel):
    agency: str
    short: str = ""
    open_opportunities: int = 0
    similar_awards_since_2018: int = 0
    note: str = ""


class MatchResponse(BaseModel):
    summary: MatchSummary
    opportunities: list[Opportunity]
    similar_companies: list[SimilarCompany] = Field(default_factory=list)
    agency_map: list[AgencyMapEntry] = Field(default_factory=list)
