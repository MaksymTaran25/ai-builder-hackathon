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

Works on **macOS, Linux, and Windows** (WSL2 or native). One-time setup from a fresh clone:

```bash
git clone https://github.com/MaksymTaran25/ai-builder-hackathon.git
cd ai-builder-hackathon && git checkout max
cd backend && uv run python setup.py        # ~10 min first time; idempotent
```

Prereqs: [uv](https://docs.astral.sh/uv/) and **Docker** (for MongoDB — `docker compose up -d`
is run for you; on macOS without Docker it falls back to Homebrew). The script installs Python
deps, starts Mongo, downloads the SBIR data (~350MB) and loads it, harvests ~900 Grants.gov
programs into your local warehouse, and pulls the local models.

```bash
uv run uvicorn app.main:app --port 8000     # start Server 1
curl localhost:8000/api/health              # → GraphQL at http://localhost:8000/graphql
```

**Local LLM by platform** — the relevance judge picks the best backend automatically:
- **Apple Silicon** → MLX (in-process, fastest). Nothing to install.
- **Linux / Windows / Intel Mac** → [Ollama](https://ollama.com): install it, then
  `ollama pull qwen3:4b`. `setup.py` pulls the model if Ollama is present.
- **Neither** → matching still works on embeddings + rules (no "Analyst" line on cards).
`/api/health` shows which is active. `LOCAL_LLM=off` disables the judge; `LOCAL_LLM_BACKEND=ollama` forces Ollama on a Mac.

**Nightly harvest** — macOS: `bash scripts/install_nightly.sh` (launchd). Linux: add to cron:
`0 0 * * * cd /path/to/backend && uv run python -m app.ingest.harvest >> data/logs/harvest.log 2>&1`.
Or just run `uv run python -m app.ingest.harvest` whenever you want fresh data.

Whole-stack check: `bash scripts/check_stack.sh` (macOS/Linux).

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

## Nightly harvester (Server 1's "smart scraper")

`app/ingest/harvest.py` sweeps Grants.gov across 15 domains (74 keyword searches), enriches
every opportunity (synopsis, award data, applicant-type eligibility, deadlines), tags it with
domains, and upserts into `govmatch.opportunities` — ~900 documents in ~17s. Runs **every
midnight** via launchd and logs each run to `harvest_runs`.

```bash
uv run python -m app.ingest.harvest              # run once now
bash scripts/install_nightly.sh                  # install the 00:00 daily job (launchd, survives reboots)
bash scripts/install_nightly.sh run-now          # trigger the scheduled job immediately
bash scripts/install_nightly.sh uninstall
```

Downstream processes query the warehouse via GraphQL, e.g.
`{ stored_opportunities(domain: "cybersecurity", eligibility: "ok", limit: 50) }` or
`{ harvest_runs(limit: 5) }` — or read the `govmatch` MongoDB directly (read-only).

## Data sources

| Source | How we use it |
|---|---|
| Grants.gov `search2` + `fetchOpportunity` | live opportunity search; award floor/ceiling + synopsis |
| SBIR.gov bulk award data (official CSV) | 39.8K awards since 2018 in MongoDB (weighted text index); powers "similar companies funded" and SBIR pathway cards (live API is down for maintenance) |
| USAspending.gov API v2 | historical awards by CFDA program: recipients, totals, medians, in-state counts |
| Curated Utah programs | state-level grants/loans/tax credits/training funds |

## Team

Max, James, Vibha — AI Builder Hackathon 2026.
