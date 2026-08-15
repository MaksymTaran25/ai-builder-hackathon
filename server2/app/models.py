"""
Pydantic Models and Schemas for Server 2
=======================================
Defines validation schemas for startup profile queries, opportunity database items,
and structured opportunity response payloads returned to Server 3.
"""

from typing import Optional, List, Union, Any, Dict
from uuid import uuid4
from pydantic import BaseModel, Field, field_validator, model_validator


# -----------------------------------------------------------------------------
# Input Models (Startup / Company Profile from Server 3)
# -----------------------------------------------------------------------------

def _normalize_to_list(val: Any) -> List[str]:
    """Helper to convert str, list, or None into a clean List[str]."""
    if val is None:
        return []
    if isinstance(val, list):
        return [str(item).strip() for item in val if str(item).strip()]
    if isinstance(val, str):
        # Support comma-separated strings or single string
        parts = [p.strip() for p in val.split(",") if p.strip()]
        return parts if parts else [val.strip()]
    return [str(val).strip()]


class StartupProfile(BaseModel):
    """
    Startup / company profile schema representing the query from Server 3.
    Supports both flexible list and string types for industry, technology, etc.
    """
    company_name: Optional[str] = Field(
        default=None,
        description="Startup or company name (e.g. 'NurseFlow AI')"
    )
    description: Optional[str] = Field(
        default=None,
        description="Natural language summary or narrative of the startup's product, mission, and technology"
    )
    industry: List[str] = Field(
        default_factory=list,
        description="Target industry domains (e.g. ['healthcare', 'software'])"
    )
    technology: List[str] = Field(
        default_factory=list,
        description="Core technologies used (e.g. ['AI', 'SaaS', 'Robotics'])"
    )
    location: Optional[str] = Field(
        default=None,
        description="Geographic base / state of operation (e.g. 'Utah')"
    )
    employees: Optional[int] = Field(
        default=None,
        description="Full-time equivalent employee headcount"
    )
    revenue: Optional[Union[float, int, str]] = Field(
        default=None,
        description="Current annual revenue or ARR (e.g. 1000000 or '$1M ARR')"
    )
    funding_stage: Optional[str] = Field(
        default=None,
        description="Company growth stage (e.g. 'seed', 'growth', 'series-a', 'bootstrapped')"
    )
    capital_raised: Optional[Union[float, int, str]] = Field(
        default=None,
        description="Total private capital raised to date (e.g. 2500000 or '$2.5M')"
    )
    funding_needed_min: Optional[Union[float, int]] = Field(
        default=None,
        description="Minimum target capital sought in USD (e.g. 500000)"
    )
    funding_needed_max: Optional[Union[float, int]] = Field(
        default=None,
        description="Maximum target capital sought in USD (e.g. 2000000)"
    )
    use_of_funds: List[str] = Field(
        default_factory=list,
        description="Intended fund use areas (e.g. ['product development', 'hospital pilots'])"
    )
    rd_activities: List[str] = Field(
        default_factory=list,
        description="Active R&D or technical milestones (e.g. ['AI development', 'workflow automation'])"
    )
    product_maturity: Optional[str] = Field(
        default=None,
        description="Product maturity status (e.g. 'prototype', 'pilot', 'commercial')"
    )
    target_customers: List[str] = Field(
        default_factory=list,
        description="Target customer personas or sectors (e.g. ['hospitals', 'defense', 'utilities'])"
    )
    
    # Aliases and backward compatibility
    name: Optional[str] = Field(default=None, exclude=True)
    story: Optional[str] = Field(default=None, exclude=True)

    @field_validator("industry", "technology", "use_of_funds", "rd_activities", "target_customers", mode="before")
    @classmethod
    def parse_flexible_lists(cls, v: Any) -> List[str]:
        return _normalize_to_list(v)

    @model_validator(mode="before")
    @classmethod
    def handle_aliases(cls, values: Any) -> Any:
        if isinstance(values, dict):
            if not values.get("company_name") and values.get("name"):
                values["company_name"] = values["name"]
            if not values.get("description") and values.get("story"):
                values["description"] = values["story"]
        return values

    model_config = {
        "json_schema_extra": {
            "example": {
                "company_name": "NurseFlow AI",
                "description": "AI software that reduces administrative work for nurses in hospitals",
                "industry": ["healthcare", "software"],
                "technology": ["AI", "SaaS"],
                "location": "Utah",
                "employees": 15,
                "revenue": 1000000,
                "funding_stage": "growth",
                "capital_raised": 2500000,
                "funding_needed_min": 500000,
                "funding_needed_max": 2000000,
                "use_of_funds": ["product development", "hospital pilots"],
                "rd_activities": ["AI development", "workflow automation"],
                "product_maturity": "commercial",
                "target_customers": ["hospitals"]
            }
        }
    }


# -----------------------------------------------------------------------------
# Data Store Model (Opportunity Item in Repository / Future MongoDB)
# -----------------------------------------------------------------------------

class Opportunity(BaseModel):
    """
    Standard schema for a government funding opportunity item.
    Corresponds directly to MongoDB document structure.
    """
    id: str
    program: str
    agency: str
    agency_short: str
    opportunity_type: str = Field(
        default="grant",
        description="Type of program: 'grant', 'sbir_grant', 'procurement', 'ota_contract', 'cooperative_agreement'"
    )
    title: str
    summary: str
    funding_min: int = Field(default=0, description="Minimum award value in USD")
    funding_max: int = Field(default=0, description="Maximum award value in USD")
    deadline: str
    days_left: int
    is_active: bool = True
    
    # Eligibility & Matching criteria
    target_industries: List[str] = Field(default_factory=list)
    target_technologies: List[str] = Field(default_factory=list)
    target_customers: List[str] = Field(default_factory=list)
    keywords: List[str] = Field(default_factory=list)
    max_employees_limit: Optional[int] = Field(default=500, description="Maximum employee threshold if SBIR/small-business restricted")
    requires_us_ownership: bool = True
    requires_active_rd: bool = False
    
    # Historical metadata
    similar_companies_funded: int = 0
    total_historical_funding: str = "$0"
    median_award: str = "$0"
    local_recipients_note: str = ""
    
    # Metadata flag
    is_demo_data: bool = Field(default=True, description="Explicitly flags whether this is synthetic demo data")


# -----------------------------------------------------------------------------
# Output / Response Models (Returned to Server 3)
# -----------------------------------------------------------------------------

class MatchResultItem(BaseModel):
    """
    Ranked and explained government funding opportunity.
    """
    id: str
    program: str
    agency: str
    opportunity_type: str
    match_score: float = Field(
        description="Calculated fit score between 0.00 and 1.00 based on weighted evaluation"
    )
    fit_tier: str = Field(
        description="Fit categorization: 'likely_fit', 'potential_fit', 'adjacent', or 'unlikely'"
    )
    funding_min: int
    funding_max: int
    deadline: str
    why_match: List[str] = Field(
        description="Detailed bullet list explaining why the startup matches this specific opportunity"
    )
    potential_concerns: List[str] = Field(
        description="Detailed bullet list of risks, eligibility checks, or verification items"
    )
    next_steps: List[str] = Field(
        description="Actionable sequential steps for the startup team"
    )


class QuerySummary(BaseModel):
    """
    High-level metrics summary of the query results.
    """
    opportunity_count: int
    agencies: List[str]
    potential_funding_min: int
    potential_funding_max: int


class OpportunityQueryResponse(BaseModel):
    """
    Canonical response payload returned by Server 2 to Server 3.
    """
    query_id: str = Field(default_factory=lambda: f"query-{uuid4().hex[:12]}")
    opportunities: List[MatchResultItem]
    summary: QuerySummary
    disclaimer: str = Field(
        default="DEMO ADVISORY: Match scores and fit tiers are analytical recommendations based on public federal data and do not constitute formal eligibility guarantees or government endorsements."
    )
