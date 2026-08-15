"""Example external process: person JSON in -> opportunity JSON out.

Sends any person/company JSON document to the GraphQL warehouse and prints the
matched opportunities. Stdlib only — copy this into any other service.

Usage:
  python examples/query_person.py            # uses the embedded sample person
  python examples/query_person.py person.json
  python examples/query_person.py person.json http://localhost:8000

Tip: include at least a sentence or two describing what the company does —
matching quality scales with description richness; one-word inputs get a
cautious, low-confidence map (by design).
"""
from __future__ import annotations

import json
import sys
import urllib.request

SAMPLE_PERSON = {
    "name": "Dana Fields",
    "company": "ClearFlow Analytics",
    "about": "We build sensor hardware and AI analytics that help municipal water utilities find leaks before they become main breaks.",
    "location": "Provo, Utah",
    "team_size": "11 people",
    "annual_revenue": "$600K",
    "total_funding": "1.2M",
    "looking_for": "$500K - $2.5M",
    "tags": ["water", "sensors", "AI"],
}

QUERY = "query M($p: JSON!) { match_person(person: $p) }"


def main() -> None:
    person = SAMPLE_PERSON
    base = "http://localhost:8000"
    if len(sys.argv) > 1:
        person = json.load(open(sys.argv[1]))
    if len(sys.argv) > 2:
        base = sys.argv[2]

    req = urllib.request.Request(
        f"{base}/graphql",
        json.dumps({"query": QUERY, "variables": {"p": person}}).encode(),
        {"content-type": "application/json"},
    )
    resp = json.load(urllib.request.urlopen(req, timeout=120))
    if resp.get("errors"):
        raise SystemExit(f"GraphQL errors: {resp['errors']}")

    result = resp["data"]["match_person"]
    json.dump(result, sys.stdout, indent=2)
    print()


if __name__ == "__main__":
    main()
