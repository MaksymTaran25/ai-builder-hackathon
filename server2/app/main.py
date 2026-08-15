"""
FastAPI Server 2: Government Opportunity Matcher & Ranker Service
================================================================
Server 2 Role in Hackathon 3-Server Architecture:
- Receives startup profile JSON query from Server 3.
- Interprets startup characteristics (domain, technology, stage, funding needs).
- Queries government opportunity data repository (currently mock, swappable with MongoDB).
- Ranks, scores, and categorizes relevant opportunities.
- Returns structured JSON response back to Server 3.
"""

import logging
from typing import Dict, Any
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware

from .models import StartupQueryRequest, OpportunityQueryResponse
from .mock_data import get_all_opportunities
from .matcher import rank_and_score_opportunities

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("server2")

# Initialize FastAPI application
app = FastAPI(
    title="Government Opportunity Map - Server 2 (Matcher & Ranker)",
    description=(
        "Microservice responsible for analyzing startup profile queries from Server 3, "
        "querying federal opportunity datasets, ranking matches, and generating "
        "advisor intelligence."
    ),
    version="1.0.0",
)

# Enable CORS for communication with Server 3 and frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", tags=["Health"])
@app.get("/health", tags=["Health"])
async def health_check() -> Dict[str, Any]:
    """
    Health check endpoint returning Server 2 operational metadata.
    """
    return {
        "status": "ok",
        "service": "server2-opportunity-matcher",
        "version": "1.0.0",
        "description": "Government Opportunity Matcher & Ranker Service",
        "datasource": "mock_data (ready for MongoDB swap)",
    }


@app.post(
    "/query",
    response_model=OpportunityQueryResponse,
    status_code=status.HTTP_200_OK,
    tags=["Opportunity Matching"],
    summary="Query and Rank Government Opportunities for a Startup",
)
async def query_opportunities(payload: StartupQueryRequest) -> OpportunityQueryResponse:
    """
    Primary API route for Server 2:
    1. Validates startup payload from Server 3.
    2. Fetches candidate opportunities from data source.
    3. Runs scoring, fit categorization, and strategic explanation engine.
    4. Returns ranked results and 90-day strategy.
    """
    logger.info(
        "Received query for startup: '%s' | Industry: '%s' | Tech: '%s'",
        payload.name or "Unnamed Startup",
        payload.industry or "Unspecified",
        payload.technology or "Unspecified"
    )

    try:
        # Step 1: Retrieve candidate opportunities from data source (Mock or MongoDB)
        raw_opportunities = get_all_opportunities()

        # Step 2: Rank and score opportunities based on startup query characteristics
        response = rank_and_score_opportunities(
            startup=payload,
            opportunities=raw_opportunities
        )

        logger.info(
            "Successfully ranked %d opportunities for startup '%s' (Top match: %s - %d%%)",
            len(response.ranked_opportunities),
            payload.name or "Startup",
            response.ranked_opportunities[0].title if response.ranked_opportunities else "None",
            response.ranked_opportunities[0].match_score if response.ranked_opportunities else 0
        )

        return response

    except Exception as exc:
        logger.error("Error processing opportunity query: %s", str(exc), exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while matching opportunities: {str(exc)}"
        )
