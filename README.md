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

### Intelligence layer — no API keys, by design

Everything runs locally: fastembed embeddings (bge-small) for semantic matching, a curated
startup→government translation table, and deterministic gates parsed from official data
(applicant-type eligibility codes, an R&D-requirement check for SBIR, a foreign-affairs
program filter). Zero keys, zero per-request cost, nothing leaves the machine, and results
are identical on every run — what you rehearse is what judges see.

(`services/llm.py` contains a dormant Claude seam behind `ANTHROPIC_API_KEY` for anyone who
wants to experiment later; the shipped product does not use it.)

## Data sources

| Source | How we use it |
|---|---|
| Grants.gov `search2` + `fetchOpportunity` | live opportunity search; award floor/ceiling + synopsis |
| SBIR.gov bulk award data (official CSV) | 39.8K awards since 2018, FTS-indexed; powers "similar companies funded" and SBIR pathway cards (live API is down for maintenance) |
| USAspending.gov API v2 | historical awards by CFDA program: recipients, totals, medians, in-state counts |
| Curated Utah programs | state-level grants/loans/tax credits/training funds |

## Team

Max, James, Vibha — AI Builder Hackathon 2026.
