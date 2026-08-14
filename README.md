# GovMatch — Government Opportunity Finder

**"I told you about my company. Now tell me what government resources I should know about — and show me why."**

A founder describes their startup in plain English. GovMatch translates startup language into
government language, searches live federal sources, and produces a **Government Opportunity Map**:
ranked opportunities with honest fit tiers, plain-English explanations, and the award history
behind each program ("who else got this money?").

## Architecture

```
Founder text
   ↓  profile extraction (Claude → structured profile, adaptive follow-ups)
   ↓  query planning   (startup language → agencies / program keywords / NAICS / SBIR topics)
   ↓  fan-out
        ├─ Grants.gov search2 API (live current + forecasted opportunities)
        ├─ SBIR.gov bulk awards, 2018+ (SQLite + FTS5, 39.8K awards) → "SBIR pathway" cards
        ├─ USAspending API v2 (award history by CFDA/ALN for each matched grant)
        └─ Curated Utah state programs (the Utah advantage)
   ↓  scoring (Claude analyst pass, or local embeddings fallback — bge-small, no key needed)
   ↓  enrichment (Grants.gov fetchOpportunity: award ranges, synopsis)
   ↓  explanations (why fit / concerns / what to verify / next steps)
   ↓  Government Opportunity Map UI
```

**Honesty by design:** when nothing scores strongly (e.g. a consumer marketplace), the map says
so up front instead of hallucinating fit, and pivots to state programs, SBA lending, and
government-as-customer paths.

## Run it

Backend (Python 3.12, [uv](https://docs.astral.sh/uv/)):

```bash
cd backend
uv sync
# one-time: download SBIR bulk data (~350MB) and build the local index
curl -L -o data/raw/sbir_award_data.csv "https://data.www.sbir.gov/awarddatapublic/award_data.csv"
uv run python -m app.ingest.sbir_ingest 2018
# run
uv run uvicorn app.main:app --port 8000
```

Frontend (Node 20+):

```bash
cd frontend
npm install
npm run dev        # http://localhost:5173, proxies /api to :8000
```

### LLM

Works out of the box with **no API key**: local embeddings (fastembed) + a deterministic
translation table handle extraction, scoring, and explanations.

For full intelligence (better extraction, analyst-grade scoring and eligibility explanations),
set:

```bash
export ANTHROPIC_API_KEY=sk-ant-...
# optional: export LLM_MODEL=claude-opus-5   (default)
```

## Data sources

| Source | How we use it |
|---|---|
| Grants.gov `search2` + `fetchOpportunity` | live opportunity search; award floor/ceiling + synopsis |
| SBIR.gov bulk award data (official CSV) | 39.8K awards since 2018, FTS-indexed; powers "similar companies funded" and SBIR pathway cards (live API is down for maintenance) |
| USAspending.gov API v2 | historical awards by CFDA program: recipients, totals, medians, in-state counts |
| Curated Utah programs | state-level grants/loans/tax credits/training funds |

## Team

Max, James, Vibha — AI Builder Hackathon 2026.
