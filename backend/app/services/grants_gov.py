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


async def search_all(statuses: str = "posted|forecasted", page: int = 500) -> list[dict[str, Any]]:
    """Every opportunity on Grants.gov for the given statuses — paginated, no keyword.
    ~1.7K records as of Aug 2026; 4 requests."""
    out: list[dict[str, Any]] = []
    async with httpx.AsyncClient() as client:
        start = 0
        while True:
            payload = {"keyword": "", "oppStatuses": statuses, "rows": page, "startRecordNum": start}
            r = await client.post(SEARCH_URL, json=payload, timeout=60)
            r.raise_for_status()
            data = r.json().get("data") or {}
            hits = data.get("oppHits") or []
            out.extend(hits)
            total = int(data.get("hitCount") or 0)
            start += page
            if not hits or start >= total:
                break
    # dedupe by id (the API can repeat across pages)
    seen: dict[str, dict] = {}
    for h in out:
        seen.setdefault(str(h.get("id")), h)
    return list(seen.values())


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


async def fetch_details_many(ids: list[str | int]) -> dict[str, dict[str, Any]]:
    """Fetch full records for many opportunities concurrently. Returns {id: data}."""

    async def one(client: httpx.AsyncClient, oid) -> tuple[str, dict]:
        r = await client.post(FETCH_URL, json={"opportunityId": int(oid)}, timeout=20)
        r.raise_for_status()
        return str(oid), r.json().get("data") or {}

    out: dict[str, dict[str, Any]] = {}
    async with httpx.AsyncClient() as client:
        results = await asyncio.gather(*(one(client, i) for i in ids), return_exceptions=True)
    for res in results:
        if not isinstance(res, Exception):
            out[res[0]] = res[1]
    return out


def link_for(opportunity_id: str | int) -> str:
    return OPP_LINK.format(id=opportunity_id)
