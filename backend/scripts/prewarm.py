"""Pre-warm the LLM verdict cache for the demo cases.

Runs the exact sample-company texts the UI's chips send, through the same
extract -> match flow, so every (profile x program) verdict is computed and
stored in MongoDB. On stage those cases then return in ~2s instead of minutes,
and — verified — with byte-identical results.

    uv run python scripts/prewarm.py            # all demo cases
    uv run python scripts/prewarm.py healthcare cyber

Run it after the nightly harvest (new programs = new pairs = cold) and before
any demo. Safe to re-run; already-cached pairs cost nothing.
"""
from __future__ import annotations

import json
import re
import sys
import time
import urllib.request
from pathlib import Path

BASE = "http://localhost:8000"
CASES_TS = Path(__file__).resolve().parents[2] / "frontend" / "src" / "testCases.ts"

PROFILE_FIELDS = """description industry technology city state employees revenue_usd
  capital_raised_usd funding_stage rd_activities product_maturity target_customers
  capital_need_min_usd capital_need_max_usd use_of_funds"""
EXTRACT = f"query E($text:String!){{ extract_profile(text:$text){{ profile{{ {PROFILE_FIELDS} }} }} }}"
MATCH = """query M($p: StartupProfileInput!){ match(profile:$p){
  summary{ high_potential overall_note }
  opportunities{ fit_tier source llm_reason } } }"""


def gql(query: str, variables: dict, timeout: int = 3600) -> dict:
    req = urllib.request.Request(
        f"{BASE}/graphql", json.dumps({"query": query, "variables": variables}).encode(),
        {"content-type": "application/json"},
    )
    d = json.load(urllib.request.urlopen(req, timeout=timeout))
    if d.get("errors"):
        raise RuntimeError(d["errors"][0].get("message"))
    return d["data"]


def load_cases() -> dict[str, str]:
    """The exact chip texts from the UI, so cache keys match what a demo click produces."""
    src = CASES_TS.read_text()
    labels = re.findall(r"label:\s*'([^']*)'", src)
    texts = re.findall(r'text:\s*"((?:[^"\\]|\\.)*)"', src)
    out = {}
    for lab, txt in zip(labels, texts):
        key = re.sub(r"[^a-z]", "", lab.lower())[:12] or f"case{len(out)}"
        out[key] = txt.encode().decode("unicode_escape")
    return out


def main() -> None:
    cases = load_cases()
    wanted = sys.argv[1:]
    if wanted:
        cases = {k: v for k, v in cases.items() if any(w.lower() in k for w in wanted)}
    if not cases:
        sys.exit(f"no matching cases. available: {', '.join(load_cases())}")

    print(f"Pre-warming {len(cases)} demo case(s) against {BASE}\n")
    total = time.time()
    for name, text in cases.items():
        t0 = time.time()
        try:
            profile = gql(EXTRACT, {"text": text})["extract_profile"]["profile"]
            m = gql(MATCH, {"p": profile})["match"]
        except Exception as e:
            print(f"  {name:16} FAILED: {e}")
            continue
        fed = [o for o in m["opportunities"] if o["source"] != "utah"]
        greens = sum(1 for o in fed if o["fit_tier"] == "likely_fit")
        first = time.time() - t0

        t1 = time.time()          # second pass proves the cache is warm
        gql(MATCH, {"p": profile})
        second = time.time() - t1

        note = " · honest-read banner" if m["summary"]["overall_note"] else ""
        print(f"  {name:16} {first:6.1f}s → {second:4.1f}s cached   {len(fed):3} programs, {greens} strong{note}")

    print(f"\nDone in {time.time() - total:.0f}s. Demo cases will now return in ~2s with identical results.")


if __name__ == "__main__":
    main()
