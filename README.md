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
        ├─ SBIR.gov bulk awards, 2018+ (MongoDB, weighted text index, 39.8K awards) → "SBIR pathway" cards
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

Backend (Python 3.12, [uv](https://docs.astral.sh/uv/), MongoDB):

```bash
# one-time: local MongoDB (no Atlas, no auth — stays fully offline)
brew tap mongodb/brew && brew trust mongodb/brew && brew install mongodb-community
brew services start mongodb/brew/mongodb-community

cd backend
uv sync
# one-time: download SBIR bulk data (~350MB) and build the text index
curl -L -o data/raw/sbir_award_data.csv "https://data.www.sbir.gov/awarddatapublic/award_data.csv"
uv run python -m app.ingest.sbir_ingest 2018
# run
uv run uvicorn app.main:app --port 8000
```

API surface: REST (`/api/*`) **and GraphQL** (`/graphql` — open it in a browser for the
interactive GraphiQL explorer). The frontend queries GraphQL first and falls back to REST.

Frontend (Node 20+):

```bash
cd frontend
npm install
npm run dev        # http://localhost:5173, proxies /api to :8000
```

### Intelligence layer — local LLM, no API keys

Retrieval + judgment, all on-device:

1. **Retrieval** — fastembed embeddings (bge-small) rank live Grants.gov hits and the SBIR corpus.
2. **Judgment** — a local LLM (**Qwen3-4B via MLX** on Apple Silicon, ~0.6s per program) reads
   each shortlisted program's actual synopsis and applicant list against the startup profile and
   returns a structured verdict: relevance, fit tier, one-line reason (shown on the card as
   "Analyst"), and whether a for-profit could apply. Blended 55/45 with the embedding score; the
   LLM can veto or move a tier by one notch, and the parsed applicant-type code stays authoritative.
3. **Deterministic gates** — eligibility codes, R&D requirement for SBIR, foreign-affairs and
   sector-mismatch filters, an honesty banner when nothing scores strongly.

Backends: MLX → Ollama (`qwen3:4b`, if MLX unavailable) → embeddings+rules. Zero keys, zero
per-request cost, nothing leaves the machine. Check which is active: `GET /api/health`.

```bash
# MLX model downloads on first start (~2.5GB, once). Optional Ollama fallback:
brew install ollama && brew services start ollama && ollama pull qwen3:4b
# disable the judge entirely: LOCAL_LLM=off
```

(`services/llm.py` also holds a dormant Claude seam behind `ANTHROPIC_API_KEY`; unused.)

## Data sources

| Source | How we use it |
|---|---|
| Grants.gov `search2` + `fetchOpportunity` | live opportunity search; award floor/ceiling + synopsis |
| SBIR.gov bulk award data (official CSV) | 39.8K awards since 2018 in MongoDB (weighted text index); powers "similar companies funded" and SBIR pathway cards (live API is down for maintenance) |
| USAspending.gov API v2 | historical awards by CFDA program: recipients, totals, medians, in-state counts |
| Curated Utah programs | state-level grants/loans/tax credits/training funds |

## Team

Max, James, Vibha — AI Builder Hackathon 2026.
