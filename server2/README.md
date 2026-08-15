# Server 2 — Government Opportunity Matcher & Ranker

Server 2 is the **Opportunity Intelligence & Matching Microservice** for the 2026 AI Builder Hackathon's 3-server architecture.

> [!NOTE]
> **DEMO DATA NOTICE**: All opportunities in the mock dataset are synthetic demo items designed to simulate federal solicitations (SBIR/STTR, ARPA-H, Grants.gov, and federal procurements) across five standard hackathon startup categories. They are intended for demonstration and hackathon testing purposes.

---

## 🏛 1. Architecture Overview

```
┌─────────────────┐        1. Query (JSON)        ┌─────────────────┐        2. Query (JSON)        ┌─────────────────┐
│    Server 1     │ ────────────────────────────> │    Server 3     │ ────────────────────────────> │    Server 2     │
│ (Frontend User  │                               │  (Aggregator /  │                               │   (Matcher &    │
│    Interface)   │ <──────────────────────────── │  Orchestrator)  │ <──────────────────────────── │     Ranker)     │
└─────────────────┘       4. Formatted UI         └─────────────────┘        3. Ranked Dossier      └─────────────────┘
                                                                                                             │
                                                                                               Query Data    │ Abstracted Repo
                                                                                                             ▼
                                                                                                  ┌───────────────────────┐
                                                                                                  │ Mock Data Repository  │
                                                                                                  │ (Swappable w/ MongoDB)│
                                                                                                  └───────────────────────┘
```

### Server 2 Responsibilities
1. **Intake**: Receive structured startup profile parameters and natural language narrative from Server 3.
2. **Repository Abstraction**: Retrieve opportunity candidates through a decoupled repository interface (`OpportunityRepository`).
3. **Filtering**: Eliminate candidates that violate hard eligibility limits (e.g. employee headcount exceeding SBIR caps).
4. **Weighted Matching**: Calculate normalized match scores (`0.00` to `1.00`), assign fit tiers (`likely_fit`, `potential_fit`, `adjacent`, `unlikely`), and synthesize detailed explanations (`why_match`, `potential_concerns`, `next_steps`).
5. **Optional LLM Layer**: Perform concept normalization and optional explanation enrichment when credentials are provided, without ever inventing or hallucinating opportunities.
6. **Response**: Return structured, strictly sorted JSON containing ranked opportunities and summary metrics.

---

## 📦 2. Installation & Setup

### Prerequisites
- Python 3.10+ (tested with Python 3.14)
- `pip` or virtual environment

### Step-by-Step Setup
```bash
cd server2

# 1. Create and activate virtual environment (if not already existing)
python3 -m venv .venv
source .venv/bin/activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. (Optional) Configure environment variables
cp .env.example .env
```

---

## 🚀 3. How to Run Server 2

Start the FastAPI application using Uvicorn:

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8002 --reload
```

- **Health Check**: [http://localhost:8002/health](http://localhost:8002/health)
- **Interactive Swagger Docs**: [http://localhost:8002/docs](http://localhost:8002/docs)
- **ReDoc Specification**: [http://localhost:8002/redoc](http://localhost:8002/redoc)

---

## 🧪 4. How to Test

Run the full automated test suite with `pytest`:

```bash
pytest tests/ -v
```

### Test Coverage Summary:
- `GET /health` verification (`status: ok`, `service: server2`).
- `POST /query` validation with full structured startup profile.
- Malformed request handling (`422 Unprocessable Entity`).
- Strict descending match score ordering (`match_score[i] >= match_score[i+1]`).
- Off-domain penalty verification (weak opportunities receive significantly lower scores).
- Full multi-domain evaluation across all 5 hackathon categories:
  1. AI Healthcare
  2. Advanced Manufacturing & Aerospace
  3. Climate & Water Innovation
  4. Cybersecurity & Critical Infrastructure
  5. Workforce & Education Technology
- `POST /query/test` convenience endpoint verification.

---

## 📡 5. API Contract & Schemas

### `GET /health`
Returns service health and operational status.

**Response (`200 OK`):**
```json
{
  "status": "ok",
  "service": "server2"
}
```

---

### `POST /query`
Receives startup parameters and returns ranked federal opportunities.

#### Example Request Payload (from Server 3):
```json
{
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
```

#### Example cURL Command:
```bash
curl -X POST "http://localhost:8002/query" \
  -H "Content-Type: application/json" \
  -d '{
    "company_name": "NurseFlow AI",
    "description": "AI software that reduces administrative work for nurses in hospitals",
    "industry": ["healthcare", "software"],
    "technology": ["AI", "SaaS"],
    "location": "Utah",
    "employees": 15,
    "revenue": 1000000,
    "funding_needed_min": 500000,
    "funding_needed_max": 2000000,
    "use_of_funds": ["product development", "hospital pilots"],
    "rd_activities": ["AI development", "workflow automation"],
    "product_maturity": "commercial",
    "target_customers": ["hospitals"]
  }'
```

#### Example Response (`200 OK`):
```json
{
  "query_id": "query-a8f3b190c12e",
  "opportunities": [
    {
      "id": "opp-nsf-seed-fund-2026",
      "program": "NSF — America's Seed Fund (Phase I/II SBIR/STTR)",
      "agency": "National Science Foundation",
      "opportunity_type": "sbir_grant",
      "match_score": 0.94,
      "fit_tier": "likely_fit",
      "funding_min": 250000,
      "funding_max": 1500000,
      "deadline": "2026-09-30",
      "why_match": [
        "Strong industry alignment with NSF priority areas (healthcare, software)",
        "Technical stack matches solicitation requirements (AI, SaaS)",
        "Active technical R&D milestones satisfy federal grant unproven innovation criteria",
        "Small business qualifying criteria satisfied (15 FTE <= 500 cap)",
        "Award size ($250,000–$1,500,000) fits requested capital range ($500,000–$2,000,000)",
        "Target customer segment aligns with agency users (hospitals)",
        "State precedent demonstrated (3 Utah recipients funded in past 2 years)"
      ],
      "potential_concerns": [
        "Verify specific annual solicitation instructions and deadlines on SAM.gov"
      ],
      "next_steps": [
        "Review official NSF solicitation topic guidance",
        "Verify active organization registration in SAM.gov and SBIR.gov",
        "Prepare 3-page Project Pitch / Specific Aims summary for Program Manager review",
        "Assemble Phase I technical proposal before 2026-09-30"
      ]
    },
    {
      "id": "opp-nih-ninr-fasttrack-2026",
      "program": "NIH / HHS — Clinical Workflow & Nursing AI Commercialization (Fast-Track)",
      "agency": "National Institutes of Health",
      "opportunity_type": "sbir_grant",
      "match_score": 0.91,
      "fit_tier": "likely_fit",
      "funding_min": 400000,
      "funding_max": 2200000,
      "deadline": "2026-10-15",
      "why_match": [
        "Strong industry alignment with NIH / HHS priority areas (healthcare, software)",
        "Technical stack matches solicitation requirements (AI, SaaS)",
        "Active technical R&D milestones satisfy federal grant unproven innovation criteria",
        "Award size ($400,000–$2,200,000) fits requested capital range ($500,000–$2,000,000)",
        "Target customer segment aligns with agency users (hospitals)"
      ],
      "potential_concerns": [
        "Verify specific annual solicitation instructions and deadlines on SAM.gov"
      ],
      "next_steps": [
        "Review official NIH / HHS solicitation topic guidance",
        "Verify active organization registration in SAM.gov and SBIR.gov",
        "Prepare 3-page Project Pitch / Specific Aims summary for Program Manager review",
        "Assemble Phase I technical proposal before 2026-10-15"
      ]
    }
  ],
  "summary": {
    "opportunity_count": 14,
    "agencies": [
      "ARPA-H",
      "CISA / DHS",
      "DARPA",
      "DOE",
      "EPA / DOE",
      "HHS / ONC",
      "NASA",
      "NIH / HHS",
      "NOAA",
      "NSF",
      "USAF / DoD",
      "USDA",
      "VA / VHA"
    ],
    "potential_funding_min": 4275000,
    "potential_funding_max": 28300000
  },
  "disclaimer": "DEMO ADVISORY: Match scores and fit tiers are analytical recommendations based on public federal data and do not constitute formal eligibility guarantees or government endorsements."
}
```

---

### `POST /query/test`
Convenience endpoint that matches using the built-in Utah AI Healthcare startup profile without requiring a JSON body in the request.

---

## ⚙️ 6. Matching Engine & Weighted Scoring

The matching engine (`app/matcher.py`) evaluates opportunities across 7 weighted dimensions:

| Dimension | Default Weight | Criteria Evaluated |
|---|:---:|---|
| **Industry Alignment** | `0.25` | Overlap with agency priority sectors |
| **Technology Alignment** | `0.25` | Overlap with software, AI, hardware, robotics, or deep-tech requirements |
| **R&D Alignment** | `0.15` | Presence of active scientific/engineering milestones vs. off-the-shelf integration |
| **Size & Eligibility** | `0.10` | Small business FTE threshold compliance (e.g. `<= 500` FTE for SBIR) |
| **Funding Need Overlap** | `0.10` | Overlap between startup capital sought and award min/max ranges |
| **Target Customers** | `0.10` | Alignment between startup customers (e.g. hospitals, utilities) and agency missions |
| **Product Maturity** | `0.05` | Prototype vs. pilot vs. commercial fit with opportunity contract type |

### Fit Tier Categorization
- `likely_fit`: Score `≥ 0.80` (High technical, domain, and eligibility alignment)
- `potential_fit`: Score `0.65 – 0.79` (Strong candidate; verify specific solicitation requirements)
- `adjacent`: Score `0.45 – 0.64` (Secondary priority; partial domain or technology overlap)
- `unlikely`: Score `< 0.45` (Deprioritized; severe domain mismatch)

---

## 🤖 7. LLM Layer & Fallback Behavior

The LLM layer (`app/llm.py`) is designed around strict architectural guarantees:

1. **Never Hallucinates Solicitations**: All opportunities evaluated by the engine originate strictly from the data repository (`app/repository.py`).
2. **Zero-Config Deterministic Mode**: If `LLM_API_KEY` is omitted, Server 2 operates in deterministic heuristic matching mode with zero runtime errors.
3. **Optional Enrichment**: When `LLM_API_KEY` is provided in `.env`, the LLM assists with semantic normalization of ambiguous startup descriptions into federal taxonomy terms.

---

## 🔄 8. Switching from Mock to MongoDB

When the hackathon team finalizes the MongoDB cluster connection and schema:

1. Install `pymongo`:
   ```bash
   pip install pymongo
   ```

2. Add connection details to `.env`:
   ```env
   MONGODB_URI=mongodb+srv://<user>:<password>@cluster.mongodb.net/
   MONGODB_DATABASE=federal_opportunities
   MONGODB_COLLECTION=opportunities
   ```

3. `get_opportunity_repository()` in `app/repository.py` will automatically detect `MONGODB_URI` and initialize `MongoOpportunityRepository`.
4. **Zero changes** to `main.py`, `matcher.py`, `models.py`, or `llm.py` are required.
