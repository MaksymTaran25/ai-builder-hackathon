"""USAspending.gov API v2 client — 'who else has received this money?'"""
from __future__ import annotations

import logging
import statistics
from typing import Any, Optional

import httpx

from ..models import HistoricalStats

log = logging.getLogger(__name__)

SEARCH_URL = "https://api.usaspending.gov/api/v2/search/spending_by_award/"
GRANT_TYPE_CODES = ["02", "03", "04", "05"]  # block/formula/project/cooperative grants

FIELDS = [
    "Award ID",
    "Recipient Name",
    "Award Amount",
    "Awarding Agency",
    "Start Date",
    "Place of Performance State Code",
    "CFDA Number",
]


async def awards_for_cfda(
    cfda_numbers: list[str],
    state: Optional[str] = None,
    years_back: int = 4,
    limit: int = 100,
) -> Optional[HistoricalStats]:
    """Recent award history for a set of CFDA/ALN program numbers."""
    if not cfda_numbers:
        return None
    payload = {
        "filters": {
            "award_type_codes": GRANT_TYPE_CODES,
            "program_numbers": cfda_numbers,
            "time_period": [{"start_date": f"{2026 - years_back}-10-01", "end_date": "2026-12-31"}],
        },
        "fields": FIELDS,
        "order": "desc",
        "sort": "Award Amount",
        "limit": limit,
        "page": 1,
    }
    try:
        async with httpx.AsyncClient() as client:
            r = await client.post(SEARCH_URL, json=payload, timeout=25)
            r.raise_for_status()
            results = r.json().get("results") or []
    except Exception:
        log.exception("USAspending lookup failed for %s", cfda_numbers)
        return None
    return _stats_from(results, state)


def _stats_from(results: list[dict[str, Any]], state: Optional[str]) -> Optional[HistoricalStats]:
    if not results:
        return None
    amounts = [r.get("Award Amount") or 0 for r in results]
    in_state = [r for r in results if state and r.get("Place of Performance State Code") == state]
    sample = [
        {
            "name": (r.get("Recipient Name") or "").title(),
            "agency": r.get("Awarding Agency") or "",
            "amount": r.get("Award Amount"),
            "year": int((r.get("Start Date") or "0")[:4]) or None,
            "program": r.get("CFDA Number") or "",
        }
        # prefer in-state recipients in the visible sample
        for r in (in_state + [x for x in results if x not in in_state])[:5]
    ]
    return HistoricalStats(
        similar_companies=len({r.get("Recipient Name") for r in results}),
        total_awarded_usd=float(sum(amounts)),
        median_award_usd=float(statistics.median(amounts)) if amounts else 0,
        in_state_recipients=len(in_state),
        sample_recipients=sample,
    )
