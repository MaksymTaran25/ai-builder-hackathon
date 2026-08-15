from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


# -------------------------------------------------------------------------
# Request Models (Received from Server 3)
# -------------------------------------------------------------------------

class StartupQueryRequest(BaseModel):
    """
    Startup / company profile query received from Server 3.
    Supports both freeform natural-language story and structured parameters.
    """
    name: Optional[str] = Field(
        default=None,
        description="Company or startup name (e.g. 'CareFlow AI')"
    )
    story: Optional[str] = Field(
        default=None,
        description="Natural language description / pitch describing the startup, technology, and goals"
    )
    industry: Optional[str] = Field(
        default=None,
        description="Primary industry domain (e.g. 'Healthcare Technology', 'Biotechnology', 'CleanTech')"
    )
    technology: Optional[str] = Field(
        default=None,
        description="Core technology stack / domain (e.g. 'Artificial Intelligence / SaaS', 'Robotics')"
    )
    location: Optional[str] = Field(
        default=None,
        description="Primary location / state of operation (e.g. 'Utah', 'CA', 'TX')"
    )
    employees: Optional[int] = Field(
        default=None,
        description="Full-time employee count"
    )
    revenue: Optional[str] = Field(
        default=None,
        description="Current annual revenue or ARR (e.g. '$1M ARR')"
    )
    funding_stage: Optional[str] = Field(
        default=None,
        description="Current venture / investment stage (e.g. 'Seed', 'Series A', 'Bootstrapped')"
    )
    capital_raised: Optional[str] = Field(
        default=None,
        description="Total private capital raised to date (e.g. '$2.5M')"
    )
    funding_need: Optional[str] = Field(
        default=None,
        description="Target capital required (e.g. '$500K–$2M')"
    )
    rd_activities: Optional[str] = Field(
        default=None,
        description="Description of current research and development or pilot efforts"
    )
    product_maturity: Optional[str] = Field(
        default=None,
        description="Stage of product development (e.g. 'Commercial with active hospital pilots')"
    )
    target_customers: Optional[str] = Field(
        default=None,
        description="Primary customer persona (e.g. 'Hospitals', 'Enterprise', 'Government')"
    )
    use_of_funds: Optional[str] = Field(
        default=None,
        description="Intended allocation of grant/contract funds (e.g. 'Product development and pilot deployment')"
    )
    filters: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Optional filter overrides (e.g. max_deadline_days, min_match_score)"
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "name": "CareFlow AI",
                "story": "We're a 15-person Utah-based AI healthcare startup building software that reduces administrative work for nurses. We have $1M ARR, have raised $2.5M, and are looking for $500K–$2M to fund product development and hospital pilots.",
                "industry": "Healthcare Technology",
                "technology": "Artificial Intelligence / SaaS",
                "location": "Utah",
                "employees": 15,
                "revenue": "$1M ARR",
                "capital_raised": "$2.5M",
                "funding_need": "$500K–$2M",
                "rd_activities": "Active product development",
                "target_customers": "Hospitals"
            }
        }
    }


# -------------------------------------------------------------------------
# Opportunity Data Models (From Data Source / Future MongoDB)
# -------------------------------------------------------------------------

class HistoricalAward(BaseModel):
    id: str
    company: str
    program: str
    agency: str
    amount: str
    year: int
    location: str
    project_title: str


class HistoricalIntelligence(BaseModel):
    similar_companies_funded: int
    total_historical_awards: str
    median_award: str
    local_recipients: str
    top_recipients_summary: str


class ActionStep(BaseModel):
    step: int
    title: str
    timeline: str
    detail: str


class DetailedOverview(BaseModel):
    why_should_i_care: str
    what_could_make_me_ineligible: List[str]
    what_should_i_verify: List[str]
    what_should_i_do_next: List[str]
    action_sequence: List[ActionStep]


class OpportunityItem(BaseModel):
    """
    Standard schema for a government funding opportunity item.
    Corresponds directly to future read-only MongoDB documents.
    """
    id: str
    title: str
    program_code: str
    agency: str
    agency_short: str
    category: str
    summary: str
    potential_value: str
    potential_value_min: Optional[float] = None
    potential_value_max: Optional[float] = None
    deadline: str
    days_left: int
    closing_soon: bool = False
    
    # Matching attributes
    target_domains: List[str] = Field(default_factory=list)
    target_technologies: List[str] = Field(default_factory=list)
    base_eligibility_criteria: List[str] = Field(default_factory=list)
    keywords: List[str] = Field(default_factory=list)
    
    # Intelligence details
    historical_intelligence: HistoricalIntelligence
    detailed_overview: DetailedOverview
    historical_awards: List[HistoricalAward] = Field(default_factory=list)


# -------------------------------------------------------------------------
# Ranked Response Models (Returned to Server 3)
# -------------------------------------------------------------------------

class RankedOpportunity(BaseModel):
    """
    Enriched opportunity result with match scoring and tailored advisor explanations.
    """
    id: str
    title: str
    program_code: str
    agency: str
    agency_short: str
    category: str
    match_score: int = Field(description="Match confidence score from 0 to 100")
    fit_level: str = Field(description="Human-readable fit label: 'Likely Fit', 'Potential Fit — Verify Eligibility', 'Adjacent Opportunity', 'Probably Not a Fit'")
    fit_level_code: str = Field(description="Code for UI styling: 'likely', 'potential', 'adjacent', 'unlikely'")
    potential_value: str
    deadline: str
    days_left: int
    closing_soon: bool
    summary: str
    why_fit: List[str] = Field(description="Bullet list of matching criteria satisfied by the startup")
    concerns: List[str] = Field(description="Bullet list of risk factors or eligibility verification items")
    historical_intelligence: HistoricalIntelligence
    detailed_overview: DetailedOverview
    historical_awards: List[HistoricalAward]


class StrategyItem(BaseModel):
    rank: str
    opportunity_id: str
    title: str
    agency: str
    potential_value: str
    rationale: str
    tag: str


class TimelineStep(BaseModel):
    month: str
    phase: str
    action: str
    deliverables: List[str]
    status: str


class SummaryMetrics(BaseModel):
    total_opportunities: int
    potential_funding_text: str
    relevant_agencies: int
    closing_within_90_days: int


class OpportunityQueryResponse(BaseModel):
    """
    Standard response payload returned by Server 2 to Server 3.
    """
    status: str = "success"
    query_startup_name: Optional[str] = None
    total_opportunities: int
    summary_metrics: SummaryMetrics
    ranked_opportunities: List[RankedOpportunity]
    strategy_recommendations: List[StrategyItem]
    sequential_timeline: List[TimelineStep]
