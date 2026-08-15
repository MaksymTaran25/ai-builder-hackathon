"""
Pytest Test Suite for Server 2
==============================
Tests the API endpoints, matching engine, schema validation, score ordering,
weak opportunity penalties, and multi-domain evaluation across all 5 hackathon categories.
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.models import OpportunityQueryResponse

client = TestClient(app)


# -----------------------------------------------------------------------------
# 1. Health Check Tests
# -----------------------------------------------------------------------------

def test_health_check():
    """Verify GET /health returns expected status and service identity."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["service"] == "server2"


# -----------------------------------------------------------------------------
# 2. Valid and Malformed /query Request Tests
# -----------------------------------------------------------------------------

def test_valid_query_request():
    """Verify POST /query with valid healthcare startup payload returns 200 and valid schema."""
    payload = {
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
    response = client.post("/query", json=payload)
    assert response.status_code == 200
    data = response.json()

    # Validate against Pydantic model
    validated = OpportunityQueryResponse(**data)
    assert validated.query_id.startswith("query-")
    assert len(validated.opportunities) > 0
    assert validated.summary.opportunity_count == len(validated.opportunities)
    assert len(validated.summary.agencies) > 0


def test_malformed_query_request():
    """Verify malformed JSON types trigger 422 Unprocessable Entity."""
    # employees must be an int or parseable int, passing invalid dictionary structure triggers 422
    payload = {
        "employees": {"invalid_nested": "not_an_int"}
    }
    response = client.post("/query", json=payload)
    assert response.status_code == 422


# -----------------------------------------------------------------------------
# 3. Match Score Ranking & Weak Opportunity Penalty Tests
# -----------------------------------------------------------------------------

def test_ranking_returns_descending_scores():
    """Verify that returned opportunities are strictly ordered from highest to lowest score."""
    payload = {
        "company_name": "CareOps AI",
        "description": "Clinical documentation software for hospital nurses",
        "industry": ["healthcare"],
        "technology": ["AI", "SaaS"]
    }
    response = client.post("/query", json=payload)
    assert response.status_code == 200
    opportunities = response.json()["opportunities"]

    scores = [item["match_score"] for item in opportunities]
    assert len(scores) >= 2
    # Ensure strictly sorted descending
    for i in range(len(scores) - 1):
        assert scores[i] >= scores[i + 1], f"Score at index {i} ({scores[i]}) is less than index {i+1} ({scores[i+1]})"


def test_weak_opportunity_receives_lower_score():
    """Verify that off-domain opportunities (e.g. nuclear physics or dairy farming) receive lower scores than matching ones."""
    payload = {
        "company_name": "NurseFlow AI",
        "description": "Hospital AI assistant for nurses",
        "industry": ["healthcare"],
        "technology": ["AI", "SaaS"]
    }
    response = client.post("/query", json=payload)
    assert response.status_code == 200
    opportunities = response.json()["opportunities"]

    # Locate NSF/NIH vs DOE nuclear opportunity
    healthcare_opps = [o for o in opportunities if "healthcare" in o["program"].lower() or "nsf" in o["program"].lower() or "nih" in o["program"].lower()]
    nuclear_opps = [o for o in opportunities if "nuclear" in o["program"].lower() or "fusion" in o["program"].lower() or "livestock" in o["program"].lower()]

    assert len(healthcare_opps) > 0
    assert len(nuclear_opps) > 0

    top_healthcare_score = max(o["match_score"] for o in healthcare_opps)
    top_nuclear_score = max(o["match_score"] for o in nuclear_opps)

    assert top_healthcare_score > top_nuclear_score
    assert top_healthcare_score >= 0.75
    assert top_nuclear_score <= 0.35


# -----------------------------------------------------------------------------
# 4. Five Hackathon Startup Category Coverage Tests
# -----------------------------------------------------------------------------

@pytest.mark.parametrize("category_name,payload,expected_agency_keyword", [
    (
        "AI Healthcare",
        {
            "company_name": "NurseFlow AI",
            "description": "AI software for hospital nurse documentation and workflow reduction",
            "industry": ["healthcare", "software"],
            "technology": ["AI", "SaaS"],
            "target_customers": ["hospitals"]
        },
        "NSF"
    ),
    (
        "Advanced Manufacturing & Aerospace",
        {
            "company_name": "AeroComposite Dynamics",
            "description": "Autonomous flight avionics and lightweight composite manufacturing for aircraft",
            "industry": ["aerospace", "manufacturing", "defense"],
            "technology": ["autonomous systems", "composites", "robotics"],
            "target_customers": ["defense primes", "air force"]
        },
        "USAF"
    ),
    (
        "Climate & Water Innovation",
        {
            "company_name": "HydroSense Analytics",
            "description": "IoT water telemetry sensors and desalination monitoring for agricultural drought resilience",
            "industry": ["climate", "water", "cleantech"],
            "technology": ["IoT sensors", "water telemetry", "SaaS"],
            "target_customers": ["utilities", "farms"]
        },
        "EPA"
    ),
    (
        "Cybersecurity",
        {
            "company_name": "ZeroShield Defense",
            "description": "Automated zero-trust cyber defense and threat intelligence for hospital and municipal SCADA grids",
            "industry": ["cybersecurity", "software"],
            "technology": ["zero trust", "AI security", "cloud security"],
            "target_customers": ["utilities", "hospitals"]
        },
        "CISA"
    ),
    (
        "Workforce & Education Technology",
        {
            "company_name": "SkillForge AI",
            "description": "Interactive simulation software and AI coaching for manufacturing and semiconductor workforce upskilling",
            "industry": ["education", "workforce", "edtech"],
            "technology": ["AI", "EdTech", "simulation"],
            "target_customers": ["community colleges", "trade schools"]
        },
        "NSF"
    ),
])
def test_five_hackathon_categories(category_name, payload, expected_agency_keyword):
    """Verify that all 5 key hackathon startup domains can query opportunities and receive relevant top-tier matches."""
    response = client.post("/query", json=payload)
    assert response.status_code == 200, f"Failed for category: {category_name}"
    data = response.json()
    
    validated = OpportunityQueryResponse(**data)
    assert len(validated.opportunities) > 0
    top_match = validated.opportunities[0]
    
    # Top match should have a high fit score
    assert top_match.match_score >= 0.70, f"Top match score ({top_match.match_score}) too low for {category_name}"
    assert top_match.fit_tier in ["likely_fit", "potential_fit"]


# -----------------------------------------------------------------------------
# 5. Quick-Test Endpoint Test
# -----------------------------------------------------------------------------

def test_query_test_endpoint():
    """Verify POST /query/test runs with default healthcare profile and returns valid dossier."""
    response = client.post("/query/test")
    assert response.status_code == 200
    data = response.json()
    validated = OpportunityQueryResponse(**data)
    assert validated.summary.opportunity_count > 0
    assert validated.opportunities[0].match_score >= 0.80
