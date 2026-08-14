"""Grants.gov search2 client (no auth required)."""
from __future__ import annotations

import asyncio
from typing import Any

import httpx

SEARCH_URL = "https://api.grants.gov/v1/api/search2"
FETCH_URL = "https://api.grants.gov/v1/api/fetchOpportunity"
OPP_LINK = "https://www.grants.gov/search-results-detail/{id}"


async def search(
    client: httpx.AsyncClient,
    keyword: str,
    rows: int = 25,
    statuses: str = "forecasted|posted",
) -> list[dict[str, Any]]:
    """One keyword search; returns raw oppHits list."""
    payload = {
        "keyword": keyword,
        "oppStatuses": statuses,
        "rows": rows,
        "startRecordNum": 0,
    }
    r = await client.post(SEARCH_URL, json=payload, timeout=20)
    r.raise_for_status()
    data = r.json()
    return (data.get("data") or {}).get("oppHits") or []


async def search_many(keywords: list[str], rows_each: int = 25) -> list[dict[str, Any]]:
    """Run several keyword searches concurrently and dedupe by opportunity id."""
    async with httpx.AsyncClient() as client:
        results = await asyncio.gather(
            *(search(client, kw, rows_each) for kw in keywords),
            return_exceptions=True,
        )
    seen: dict[str, dict] = {}
    for kw, res in zip(keywords, results):
        if isinstance(res, Exception):
            continue
        for hit in res:
            hid = str(hit.get("id"))
            if hid not in seen:
                hit["_matched_keywords"] = [kw]
                seen[hid] = hit
            else:
                seen[hid]["_matched_keywords"].append(kw)
    return list(seen.values())


async def fetch_details(opportunity_id: str | int) -> dict[str, Any]:
    """Full record for one opportunity: synopsis, award floor/ceiling, description."""
    async with httpx.AsyncClient() as client:
        r = await client.post(FETCH_URL, json={"opportunityId": int(opportunity_id)}, timeout=20)
        r.raise_for_status()
        return r.json().get("data") or {}


def link_for(opportunity_id: str | int) -> str:
    return OPP_LINK.format(id=opportunity_id)
