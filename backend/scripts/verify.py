"""Demo-readiness gate: runs the judged test cases + edge cases against a running
backend (GraphQL-only API) and checks invariants.
Usage: uv run python scripts/verify.py [base_url]
"""
from __future__ import annotations

import json
import re
import sys
import time
import urllib.error
import urllib.request

BASE = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8000"

PROFILE_FIELDS = """description industry technology city state employees revenue_usd
  capital_raised_usd funding_stage rd_activities product_maturity target_customers
  capital_need_min_usd capital_need_max_usd use_of_funds"""

EXTRACT_QUERY = f"""query E($text: String!) {{ extract_profile(text: $text) {{
  profile {{ {PROFILE_FIELDS} }} followups {{ field question }} }} }}"""

MATCH_QUERY = """query M($p: StartupProfileInput!) { match(profile: $p) {
  summary { high_potential total_potential_value_usd agencies closing_within_90_days overall_note }
  opportunities { source source_id title agency fit_tier score close_date url eligibility_flag
    history { similar_companies in_state_recipients } }
  similar_companies { name state total_usd }
  agency_map { short open_opportunities }
} }"""

CASES = {
    "healthcare": "We're a 15-person Utah company developing AI-powered software that helps hospitals reduce administrative work for nurses. We've raised $2.5M, have $1M in ARR, and are looking for $500K–$2M of non-dilutive capital to fund product development and hospital pilots.",
    "manufacturing": "We're a Utah hardware startup doing advanced manufacturing of lightweight aerospace components. 35 employees, $3M revenue, $8M raised. We need $2M–$5M for manufacturing scale-up and R&D.",
    "water": "We're a 10-person Utah startup with a sensor and AI platform that reduces municipal water loss. $500K revenue, $1.5M raised. Looking for $500K–$3M for product development and municipal pilots.",
    "cyber": "We're a Utah cybersecurity startup building AI-powered threat detection for small and mid-sized organizations. 22 employees, $2M ARR, $5M raised. We need $1M–$3M for R&D and federal/commercial expansion.",
    "youth": "We're a Utah technology startup running a marketplace that connects parents with local youth activities and enrichment programs. 8 employees, $750K revenue, $1M raised. Looking for $250K–$1M for expansion and technology development.",
    "vague": "We make an app.",
    "idaho": "We're a Boise, Idaho robotics company doing agricultural automation research. 12 employees, $400K revenue. Need $1M for R&D.",
}

passed, failed = 0, 0


def check(name: str, cond: bool, detail: str = ""):
    global passed, failed
    if cond:
        passed += 1
        print(f"  PASS  {name}")
    else:
        failed += 1
        print(f"  FAIL  {name}  {detail}")


def _post(path: str, body: dict, timeout: int = 90) -> dict:
    req = urllib.request.Request(
        f"{BASE}{path}", json.dumps(body).encode(), {"content-type": "application/json"}
    )
    return json.load(urllib.request.urlopen(req, timeout=timeout))


def gql(query: str, variables: dict) -> dict:
    d = _post("/graphql", {"query": query, "variables": variables})
    if d.get("errors"):
        raise RuntimeError(f"graphql errors: {json.dumps(d['errors'])[:200]}")
    return d["data"]


def extract(text: str) -> dict:
    return gql(EXTRACT_QUERY, {"text": text})["extract_profile"]


def match(profile: dict) -> dict:
    return gql(MATCH_QUERY, {"p": profile})["match"]


def run_case(name: str, text: str) -> dict:
    print(f"\n== {name} ==")
    t0 = time.time()
    ex = extract(text)
    profile = ex["profile"]
    d = match(profile)
    dt = time.time() - t0
    opps = d["opportunities"]
    fed = [o for o in opps if o["source"] != "utah"]
    ut = [o for o in opps if o["source"] == "utah"]

    check("responds", bool(opps), "empty opportunity list")
    check(f"latency {dt:.1f}s < 300s", dt < 300)
    tier_rank = {"likely_fit": 3, "potential_fit": 2, "adjacent": 1, "not_a_fit": 0}
    keys = [(tier_rank[o["fit_tier"]], o["score"]) for o in fed]
    check("sorted by tier then score", keys == sorted(keys, reverse=True))
    check(
        "no ineligible likely-fits",
        all(o["fit_tier"] != "likely_fit" or o.get("eligibility_flag") in ("ok", "verify", None) for o in fed),
    )
    check(
        "close dates parse or null",
        all(not o.get("close_date") or re.match(r"\d{2}/\d{2}/\d{4}", o["close_date"]) for o in fed),
        str([o.get("close_date") for o in fed if o.get("close_date")][:3]),
    )
    check("urls https", all((o.get("url") or "https://x").startswith("https://") for o in opps))

    if name == "vague":
        check("followups fire for vague input", len(ex["followups"]) >= 2, f"got {len(ex['followups'])}")
    if name == "youth":
        check("honesty note fires", bool(d["summary"]["overall_note"]))
        check("no green badges", all(o["fit_tier"] != "likely_fit" for o in opps))
    elif name in ("healthcare", "manufacturing", "cyber"):
        check("no false honesty note", not d["summary"]["overall_note"], d["summary"]["overall_note"][:60])
        check("has likely fits", any(o["fit_tier"] == "likely_fit" for o in fed))
        check("has history on a top card", any(o.get("history") for o in fed[:6]))
        check("similar companies present", len(d.get("similar_companies") or []) >= 3)
    if name == "idaho":
        check("no Utah section for Idaho company", not ut)
        check("state extracted ID", profile.get("state") == "ID", str(profile.get("state")))
    elif name != "vague":
        check("Utah section for UT company", len(ut) > 0)
    return d


for name, text in CASES.items():
    try:
        run_case(name, text)
    except Exception as e:
        failed += 1
        print(f"  FAIL  {name} crashed: {e}")

# REST data endpoints must be gone (GraphQL-only by design)
print("\n== graphql-only surface ==")
try:
    _post("/api/match", {"description": "x"}, timeout=10)
    check("REST /api/match removed", False, "endpoint still exists")
except urllib.error.HTTPError as e:
    check("REST /api/match removed", e.code in (404, 405), f"status {e.code}")
except Exception as e:
    check("REST /api/match removed", False, str(e)[:80])

# warehouse: everything fetched must be stored in MongoDB and queryable
print("\n== warehouse (MongoDB via GraphQL) ==")
try:
    w = gql(
        """query { stored_opportunities(limit: 5) match_runs(limit: 3) award_history(limit: 3)
             sbir_awards(search: "artificial intelligence", state: "UT", limit: 3) {
               company state award_amount } }""",
        {},
    )
    check("stored_opportunities populated", len(w["stored_opportunities"]) > 0)
    check("match_runs recorded", len(w["match_runs"]) > 0)
    check("award_history cached", len(w["award_history"]) > 0)
    check("sbir corpus queryable", len(w["sbir_awards"]) > 0)
    hv = gql("query { harvest_runs(limit: 1) stored_opportunities(domain: \"cybersecurity\", limit: 200) }", {})
    check("harvester has run", len(hv["harvest_runs"]) > 0)
    check("warehouse stocked (>=100 cyber-domain docs)", len(hv["stored_opportunities"]) >= 100, str(len(hv["stored_opportunities"])))
    check(
        "sbir state filter works",
        all(a["state"] == "UT" for a in w["sbir_awards"]),
        str(w["sbir_awards"])[:100],
    )
except Exception as e:
    check("warehouse queries", False, str(e)[:150])

# concurrency: 3 parallel matches must all succeed
print("\n== concurrency (3 parallel) ==")
import concurrent.futures as cf

profile = extract(CASES["healthcare"])["profile"]
t0 = time.time()
with cf.ThreadPoolExecutor(3) as pool:
    results = list(pool.map(lambda _: match(profile), range(3)))
check(f"3 parallel matches ok ({time.time()-t0:.1f}s)", all(r["opportunities"] for r in results))

print(f"\n{'='*40}\n{passed} passed, {failed} failed")
sys.exit(1 if failed else 0)
