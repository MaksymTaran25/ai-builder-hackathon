"""
FastAPI Server 2: Government Opportunity Matcher & Ranker
=========================================================
Server 2 Responsibilities in 3-Server Architecture:
- Receives startup profile query from Server 3.
- Retrieves candidate government opportunities from OpportunityRepository (Mock/MongoDB).
- Runs weighted matching and explanation engine (with optional LLM normalization).
- Returns structured, ranked JSON response to Server 3.
"""

import logging
from typing import Dict, Any, Optional
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware

from .models import (
    StartupProfile,
    OpportunityQueryResponse,
)
from .repository import OpportunityRepository, get_opportunity_repository
from .matcher import match_and_rank_opportunities
from .llm import BaseLLMClient, get_llm_client

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("server2.api")

# Initialize FastAPI App
app = FastAPI(
    title="Government Opportunity Map — Server 2 (Matcher & Ranker)",
    description=(
        "Microservice responsible for analyzing startup profile queries from Server 3, "
        "querying federal opportunity datasets, ranking matches via weighted multi-factor scoring, "
        "and returning structured advisor dossiers."
    ),
    version="2.0.0",
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get(
    "/health",
    tags=["Health"],
    summary="Health Check",
    response_model=Dict[str, str],
)
@app.get("/", tags=["Health"], include_in_schema=False)
async def health_check() -> Dict[str, str]:
    """
    Returns health status of Server 2.
    """
    return {
        "status": "ok",
        "service": "server2"
    }


@app.post(
    "/query",
    response_model=OpportunityQueryResponse,
    status_code=status.HTTP_200_OK,
    tags=["Matching"],
    summary="Query and rank federal opportunities for a startup profile",
)
async def query_opportunities(
    profile: StartupProfile,
    repo: OpportunityRepository = Depends(get_opportunity_repository),
    llm: BaseLLMClient = Depends(get_llm_client),
) -> OpportunityQueryResponse:
    """
    Primary API endpoint for Server 2:
    1. Validates startup profile JSON received from Server 3.
    2. Retrieves candidate opportunities from the repository.
    3. Runs weighted matching, scoring (0.0 to 1.0), and fit tier categorization.
    4. Returns structured JSON containing ranked opportunities and summary metrics.
    """
    logger.info(
        "Received query for startup: '%s' | Industry: %s | Tech: %s",
        profile.company_name or "Unnamed Startup",
        profile.industry,
        profile.technology
    )

    try:
        # Step 1: Query candidates from repository abstraction
        candidates = repo.search_candidates(profile)
        logger.info("Found %d candidate opportunities from repository.", len(candidates))

        # Step 2: Rank and explain matches using weighted scoring engine
        response = match_and_rank_opportunities(
            profile=profile,
            candidates=candidates,
            llm_client=llm
        )

        top_opp = response.opportunities[0] if response.opportunities else None
        logger.info(
            "Ranked %d opportunities. Top match: '%s' (Score: %.2f | Tier: %s)",
            len(response.opportunities),
            top_opp.program if top_opp else "None",
            top_opp.match_score if top_opp else 0.0,
            top_opp.fit_tier if top_opp else "N/A"
        )

        return response

    except Exception as exc:
        logger.error("Error processing opportunity matching query: %s", exc, exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while evaluating opportunities: {str(exc)}"
        )


@app.post(
    "/query/test",
    response_model=OpportunityQueryResponse,
    status_code=status.HTTP_200_OK,
    tags=["Testing"],
    summary="Quick-test matching using the default hackathon AI healthcare startup",
)
async def query_test_example(
    repo: OpportunityRepository = Depends(get_opportunity_repository),
    llm: BaseLLMClient = Depends(get_llm_client),
) -> OpportunityQueryResponse:
    """
    Convenience endpoint for quickly testing the service without manually writing a JSON body.
    Uses the default Utah-based NurseFlow AI healthcare startup profile.
    """
    example_profile = StartupProfile(
        company_name="NurseFlow AI",
        description="AI software that reduces administrative work for nurses in hospitals. We have $1M ARR, 15 FTEs in Utah, and are looking for non-dilutive capital to scale hospital pilots.",
        industry=["healthcare", "software"],
        technology=["AI", "SaaS"],
        location="Utah",
        employees=15,
        revenue=1000000,
        funding_stage="growth",
        capital_raised=2500000,
        funding_needed_min=500000,
        funding_needed_max=2000000,
        use_of_funds=["product development", "hospital pilots"],
        rd_activities=["AI development", "workflow automation"],
        product_maturity="commercial",
        target_customers=["hospitals"]
    )

    candidates = repo.search_candidates(example_profile)
    return match_and_rank_opportunities(
        profile=example_profile,
        candidates=candidates,
        llm_client=llm
    )
