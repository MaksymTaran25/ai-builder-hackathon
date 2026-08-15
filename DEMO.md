# Demo script (~3 min)

## Setup (before judges arrive)
```bash
# terminal 1
cd backend && uv run uvicorn app.main:app --port 8000
# terminal 2
cd frontend && npm run dev
```
Open http://localhost:5173. **No API keys — that's deliberate.** All intelligence runs
locally (embeddings + rules over official government data). Sanity check before judging:
`cd backend && uv run python scripts/verify.py` — must end `0 failed`.

## The story

**1. The problem (15s).** "A founder thinks in terms of their product and customers. The
government thinks in agencies, CFDA numbers, and eligibility categories. Billions go unclaimed
because founders never find out they qualify."

**2. Live: AI Healthcare case (60s).** Click the 🏥 chip → Find my opportunities.
- Point at the extracted profile chips: "No forms — it read the description like an analyst."
- Build the map. While loading: "It's translating startup language into government language,
  searching Grants.gov live, and joining three federal datasets."
- Top card: **Research Grants in Clinical Informatics (NIH)** — fit tier, match %, award range,
  deadline, and the four explanations (why / concerns / verify / next steps).
- **The differentiator** — "Who else has received this money?": recipients, median award,
  **3 recipients in Utah, including University of Utah**. "This isn't a search result — it's
  underwriting evidence from USAspending."
- Scroll: **✓ Small businesses eligible** badges — "We parse the official applicant types; when a
  program only funds nonprofits or universities, we say a for-profit likely can't apply instead
  of wasting the founder's week."

**3. Similar companies + agency map (30s).** "Here are SBIR recipients working on similar
technology — **Epitel, a Utah company, $3.7M from HHS**. Proof this path works from where you
are. And the agency map shows where your people are: NIH for grants, HHS/DOD/NSF for SBIR."

**4. The honesty trap (30s).** Start over → 👨‍👩‍👧 Youth Marketplace chip → run.
- **⚖️ Honest read banner**: "Federal grants are a weak fit for this business model."
- "Zero fake 'likely fits'. SBIR requires R&D — a consumer marketplace doesn't qualify, so we
  say so, and pivot to Utah state programs, SBA lending, and government-as-customer instead.
  We'd rather be trusted than impressive."

**5. Utah advantage + close (30s).** Scroll to 🏔️ Utah programs. "Federal + state in one map.
Export the report, hand it to your accountant. This is a funding analyst for every startup —
today it's grants and SBIR; the same architecture extends to loans, procurement, and incentives."

## If wifi dies
Everything except Grants.gov/USAspending is local (SBIR SQLite + embeddings). The map still
builds with SBIR pathways, similar companies, and Utah programs.

## Q&A ammo
- **Data**: Grants.gov search2 + fetchOpportunity (live), SBIR bulk awards 2018+ (39.8K, local
  FTS), USAspending v2 by CFDA (live), curated Utah programs. All official, all free, no keys.
- **AI layer**: fully local — semantic embeddings (bge-small) + a startup→government
  translation table + deterministic gates (eligibility codes, R&D requirement, foreign-affairs
  filter). **Zero API keys, zero per-request cost, zero data leaves the machine, works on
  hostile wifi.** An LLM seam exists in the code if a team ever wants it; we chose not to need it.
- **Eligibility**: parsed from the official applicantTypes codes on each listing (small business
  = code 23). Framed as guidance, never as a determination.
- **Why not RAG over everything?** 2-4 sources done deeply beats shallow everything — per the
  brief. The CFDA number is the join key that turns a listing into evidence.
