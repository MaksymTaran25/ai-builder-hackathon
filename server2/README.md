# Server 2 — Government Opportunity Matcher & Ranker

Server 2 is the **Opportunity Intelligence & Matching Microservice** in our hackathon's 3-server architecture.

---

## 🏛 Architecture Context

```
┌──────────────┐         JSON Query          ┌──────────────┐         JSON Query          ┌──────────────┐
│   Server 1   │ ──────────────────────────> │   Server 3   │ ──────────────────────────> │   Server 2   │
│  (Frontend/  │                             │ (Aggregator/ │                             │  (Matcher &  │
│   Client)    │ <────────────────────────── │ Orchestrator)│ <────────────────────────── │   Ranker)    │
└──────────────┘       Ranked Dossier        └──────────────┘       Structured JSON       └──────────────┘
                                                                                                 │
                                                                                           Query │ Data Source
                                                                                                 ▼
                                                                                          ┌──────────────┐
                                                                                          │ Mock Data /  │
                                                                                          │   MongoDB    │
                                                                                          └──────────────┘
```

### Server 2 Responsibilities:
1. Receive a structured or natural-language startup profile JSON query from **Server 3**.
2. Interpret the startup's funding needs, industry domain, technology stack, and business parameters.
3. Query the federal opportunities dataset (currently in-memory mock repository, MongoDB-ready).
4. Score, categorize fit levels, synthesize tailored advisor rationale, and rank relevant opportunities.
5. Return structured JSON results and a 90-day sequential strategy back to **Server 3**.

---

## 🚀 Running Server 2 Locally

### 1. Activate Environment & Run Uvicorn
Using the preconfigured `.venv`:
```bash
cd server2
.venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8002 --reload
```

Or using system Python / venv:
```bash
cd server2
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8002 --reload
```

### 2. Interactive Documentation
Once running, visit:
- Swagger UI: [http://localhost:8002/docs](http://localhost:8002/docs)
- ReDoc: [http://localhost:8002/redoc](http://localhost:8002/redoc)
- Health Check: [http://localhost:8002/health](http://localhost:8002/health)

---

## 📡 API Endpoints

### 1. Health Check
`GET /health` or `GET /`

**Response (`200 OK`):**
```json
{
  "status": "ok",
  "service": "server2-opportunity-matcher",
  "version": "1.0.0",
  "description": "Government Opportunity Matcher & Ranker Service",
  "datasource": "mock_data (ready for MongoDB swap)"
}
```

---

### 2. Query & Rank Opportunities
`POST /query`

#### Request Payload (from Server 3):
```json
{
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
```

#### Example cURL Command:
```bash
curl -X POST "http://localhost:8002/query" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "CareFlow AI",
    "story": "We are a 15-person Utah-based AI healthcare startup building software that reduces administrative work for nurses.",
    "industry": "Healthcare Technology",
    "technology": "Artificial Intelligence / SaaS",
    "location": "Utah",
    "employees": 15,
    "revenue": "$1M ARR",
    "funding_need": "$500K-$2M"
  }'
```

#### Response Structure:
```json
{
  "status": "success",
  "query_startup_name": "CareFlow AI",
  "total_opportunities": 7,
  "summary_metrics": {
    "total_opportunities": 7,
    "potential_funding_text": "$3.2M+",
    "relevant_agencies": 6,
    "closing_within_90_days": 4
  },
  "ranked_opportunities": [
    {
      "id": "nsf-seed-fund-2026",
      "title": "NSF — America's Seed Fund (Phase I/II SBIR/STTR)",
      "program_code": "NSF-SBIR-2026-04",
      "agency": "National Science Foundation",
      "agency_short": "NSF",
      "category": "R&D Grant",
      "match_score": 92,
      "fit_level": "Likely Fit",
      "fit_level_code": "likely",
      "potential_value": "$250K–$1.5M",
      "deadline": "September 30, 2026",
      "days_left": 47,
      "closing_soon": true,
      "summary": "Non-dilutive federal funding supporting early-stage startups conducting unproven technical R&D...",
      "why_fit": [
        "AI technology & software algorithm alignment",
        "Direct healthcare workflow & clinical impact alignment",
        "Small business qualifying criteria satisfied (15 FTE < 500 cap)",
        "Active technical R&D and commercialization potential",
        "Demonstrated state precedent (3 Utah recipients)"
      ],
      "concerns": [
        "Verify current solicitation requirements for mandatory Project Pitch",
        "Confirm company eligibility and active SAM.gov UEI registration"
      ],
      "historical_intelligence": { ... },
      "detailed_overview": { ... },
      "historical_awards": [ ... ]
    },
    ...
  ],
  "strategy_recommendations": [ ... ],
  "sequential_timeline": [ ... ]
}
```

---

## 🔌 Live data: wired to Server 1 (GovMatch)

Server 2 now queries **Server 1's GraphQL API** (`GOVMATCH_URL`, default `http://localhost:8000`)
instead of the in-memory mocks. Server 1 owns the MongoDB warehouse (900+ nightly-harvested
Grants.gov opportunities, 39.8K SBIR awards, USAspending history) and the matching intelligence
(local LLM relevance judge on MLX + embeddings + eligibility gates). `app/govmatch_client.py`
reshapes Server 1's `match_person` result into this service's response contract — **no changes
to `models.py`, the `/query` request or response schema.**

- `why_fit`, `concerns`, `historical_intelligence`, `historical_awards` are real (USAspending / SBIR data)
- `strategy_recommendations` and `sequential_timeline` are generated from the actual top matches
- `filters.max_deadline_days` and `filters.min_match_score` are honored
- If Server 1 is unreachable, Server 2 **automatically falls back to `mock_data.py`** and
  `/health` says so (`datasource`), so this service never stops answering.

Run Server 1 first (see repo root `README.md`: MongoDB + `cd backend && uv run uvicorn app.main:app --port 8000`),
then Server 2 as above. Check `GET /health` — `datasource` should mention `GovMatch Server 1`.

