"""Normalize an arbitrary person/company JSON document into a StartupProfile.

Other processes send whatever field names they have; we map the common variants,
and anything expressed only as free text falls back to the extraction pipeline.
"""
from __future__ import annotations

import re
from typing import Any, Optional

from ..models import StartupProfile
from . import llm

TEXT_KEYS = ("description", "about", "story", "bio", "summary", "company_description", "pitch", "what_we_do")
INDUSTRY_KEYS = ("industry", "sector", "vertical", "market")
STATE_KEYS = ("state", "location", "region", "city", "address", "based_in", "headquarters")
EMPLOYEE_KEYS = ("employees", "team_size", "headcount", "number_employees", "num_employees", "size")
REVENUE_KEYS = ("revenue_usd", "revenue", "arr", "annual_revenue", "sales")
RAISED_KEYS = ("capital_raised_usd", "raised", "funding_raised", "total_funding", "capital_raised")
NEED_KEYS = ("capital_need_max_usd", "need", "funding_need", "looking_for", "seeking", "ask", "capital_need")
TECH_KEYS = ("technology", "tech", "technologies", "keywords", "tags", "focus_areas")

_STATE_CODES = {
    "alabama": "AL", "alaska": "AK", "arizona": "AZ", "arkansas": "AR", "california": "CA",
    "colorado": "CO", "connecticut": "CT", "delaware": "DE", "florida": "FL", "georgia": "GA",
    "hawaii": "HI", "idaho": "ID", "illinois": "IL", "indiana": "IN", "iowa": "IA",
    "kansas": "KS", "kentucky": "KY", "louisiana": "LA", "maine": "ME", "maryland": "MD",
    "massachusetts": "MA", "michigan": "MI", "minnesota": "MN", "mississippi": "MS",
    "missouri": "MO", "montana": "MT", "nebraska": "NE", "nevada": "NV", "new hampshire": "NH",
    "new jersey": "NJ", "new mexico": "NM", "new york": "NY", "north carolina": "NC",
    "north dakota": "ND", "ohio": "OH", "oklahoma": "OK", "oregon": "OR", "pennsylvania": "PA",
    "rhode island": "RI", "south carolina": "SC", "south dakota": "SD", "tennessee": "TN",
    "texas": "TX", "utah": "UT", "vermont": "VT", "virginia": "VA", "washington": "WA",
    "west virginia": "WV", "wisconsin": "WI", "wyoming": "WY",
}


def _first(d: dict, keys: tuple) -> Any:
    for k in keys:
        for kk in (k, k.upper(), k.title()):
            if kk in d and d[kk] not in (None, "", []):
                return d[kk]
    lower = {k.lower(): v for k, v in d.items()}
    for k in keys:
        if k in lower and lower[k] not in (None, "", []):
            return lower[k]
    return None


def _money(v: Any) -> Optional[int]:
    if v is None:
        return None
    if isinstance(v, (int, float)):
        return int(v)
    s = str(v).replace(",", "").replace("$", "").strip().lower()
    m = re.match(r"([\d.]+)\s*([kmb])?", s)
    if not m or not m.group(1):
        return None
    mult = {"k": 1e3, "m": 1e6, "b": 1e9}.get(m.group(2) or "", 1)
    try:
        return int(float(m.group(1)) * mult)
    except ValueError:
        return None


def _money_range(v: Any) -> tuple[Optional[int], Optional[int]]:
    if isinstance(v, dict):
        return _money(_first(v, ("min", "low", "from"))), _money(_first(v, ("max", "high", "to")))
    if isinstance(v, (list, tuple)) and len(v) == 2:
        return _money(v[0]), _money(v[1])
    s = str(v)
    parts = re.split(r"\s*(?:-|–|—|to)\s*", s)
    if len(parts) == 2:
        return _money(parts[0]), _money(parts[1])
    return None, _money(v)


def _state(v: Any) -> Optional[str]:
    s = str(v).strip()
    m = re.search(r"\b([A-Z]{2})\b", s)
    if m and m.group(1) in _STATE_CODES.values():
        return m.group(1)
    low = s.lower()
    for name, code in _STATE_CODES.items():
        if name in low:
            return code
    return None


def _intish(v: Any) -> Optional[int]:
    try:
        return int(re.sub(r"[^\d]", "", str(v)) or 0) or None
    except ValueError:
        return None


async def to_profile(person: dict) -> StartupProfile:
    """Map arbitrary person JSON -> StartupProfile. Free text is extracted first,
    then explicit structured fields override whatever extraction guessed."""
    text_parts = [str(v) for k in TEXT_KEYS if (v := _first(person, (k,)))]
    text = " ".join(text_parts) or str(person)

    profile, _ = await llm.extract_profile(text)

    if v := _first(person, INDUSTRY_KEYS):
        profile.industry = str(v)
    if v := _first(person, STATE_KEYS):
        profile.state = _state(v) or profile.state
    if v := _first(person, EMPLOYEE_KEYS):
        profile.employees = _intish(v) or profile.employees
    if v := _first(person, REVENUE_KEYS):
        profile.revenue_usd = _money(v) or profile.revenue_usd
    if v := _first(person, RAISED_KEYS):
        profile.capital_raised_usd = _money(v) or profile.capital_raised_usd
    if v := _first(person, NEED_KEYS):
        lo, hi = _money_range(v)
        profile.capital_need_min_usd = lo or profile.capital_need_min_usd
        profile.capital_need_max_usd = hi or profile.capital_need_max_usd
    if v := _first(person, TECH_KEYS):
        profile.technology = [str(x) for x in v] if isinstance(v, list) else [str(v)]

    return profile
