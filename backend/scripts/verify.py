"""Demo-readiness gate: runs the judged test cases + edge cases against a running
backend and checks invariants. Usage: uv run python scripts/verify.py [base_url]
"""
from __future__ import annotations

import json
import re
import sys
import time
import urllib.request

BASE = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8000"

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


def post(path: str, body: dict, timeout: int = 90) -> dict:
    req = urllib.request.Request(
        f"{BASE}{path}", json.dumps(body).encode(), {"content-type": "application/json"}
    )
    return json.load(urllib.request.urlopen(req, timeout=timeout))


def run_case(name: str, text: str) -> dict:
    print(f"\n== {name} ==")
    t0 = time.time()
    ex = post("/api/profile/extract", {"text": text})
    profile = ex["profile"]
    d = post("/api/match", profile)
    dt = time.time() - t0
    opps = d["opportunities"]
    fed = [o for o in opps if o["source"] != "utah"]
    ut = [o for o in opps if o["source"] == "utah"]

    check("responds", bool(opps), "empty opportunity list")
    check(f"latency {dt:.1f}s < 15s", dt < 15)
    scores = [o["score"] for o in fed]
    check("sorted by score", scores == sorted(scores, reverse=True))
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

# GraphQL parity: same profile through /graphql must equal REST
print("\n== graphql parity ==")
gq = """query M($p: StartupProfileInput!) { match(profile: $p) {
  summary { high_potential } opportunities { source_id fit_tier score } } }"""
p_hc = post("/api/profile/extract", {"text": CASES["healthcare"]})["profile"]
rest = post("/api/match", p_hc)
graph = post("/graphql", {"query": gq, "variables": {"p": p_hc}})
if graph.get("errors"):
    check("graphql executes", False, str(graph["errors"])[:120])
else:
    gm = graph["data"]["match"]
    check("graphql executes", True)
    check(
        "graphql == rest (ids + tiers)",
        [(o["source_id"], o["fit_tier"]) for o in gm["opportunities"]]
        == [(o["source_id"], o["fit_tier"]) for o in rest["opportunities"]],
    )
    check("graphql tier values match REST format", all(
        o["fit_tier"] in ("likely_fit", "potential_fit", "adjacent", "not_a_fit")
        for o in gm["opportunities"]
    ))

# concurrency: 3 parallel matches must all succeed
print("\n== concurrency (3 parallel) ==")
import concurrent.futures as cf

profile = post("/api/profile/extract", {"text": CASES["healthcare"]})["profile"]
t0 = time.time()
with cf.ThreadPoolExecutor(3) as pool:
    results = list(pool.map(lambda _: post("/api/match", profile), range(3)))
check(f"3 parallel matches ok ({time.time()-t0:.1f}s)", all(r["opportunities"] for r in results))

print(f"\n{'='*40}\n{passed} passed, {failed} failed")
sys.exit(1 if failed else 0)
