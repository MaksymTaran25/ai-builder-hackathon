"""SBIR/STTR award history from the local SQLite cache (bulk data, 2018+).

The live SBIR API is down for maintenance (Aug 2026), so awards come from the
official bulk CSV ingested by app.ingest.sbir_ingest. Used two ways:
1. history stats for "who got funded for similar technology"
2. synthesized "SBIR/STTR pathway" opportunity cards per top funding agency
"""
from __future__ import annotations

import logging
import re
import sqlite3
import statistics
from pathlib import Path
from typing import Optional

from ..models import HistoricalStats, Opportunity

log = logging.getLogger(__name__)

DB_PATH = Path(__file__).resolve().parents[2] / "data" / "gov.db"

AGENCY_SBIR_LINKS = {
    "Department of Health and Human Services": "https://seed.nih.gov/",
    "National Science Foundation": "https://seedfund.nsf.gov/",
    "Department of War": "https://www.dodsbirsttr.mil/",
    "Department of Defense": "https://www.dodsbirsttr.mil/",
    "National Aeronautics and Space Administration": "https://sbir.nasa.gov/",
    "Department of Energy": "https://science.osti.gov/sbir",
    "Department of Homeland Security": "https://www.dhs.gov/science-and-technology/sbir",
    "Environmental Protection Agency": "https://www.epa.gov/sbir",
    "United States Dept. of Agriculture": "https://www.nifa.usda.gov/grants/programs/sbir-sttr",
}


def _connect() -> Optional[sqlite3.Connection]:
    if not DB_PATH.exists():
        return None
    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row
    return con


def _fts_query(topics: list[str]) -> str:
    """Build an OR-of-phrases FTS5 query, sanitized."""
    phrases = []
    for t in topics:
        clean = re.sub(r'[^a-zA-Z0-9 ]', ' ', t).strip()
        if clean:
            phrases.append(f'"{clean}"')
    return " OR ".join(phrases)


def similar_awards(topics: list[str], state: Optional[str], limit: int = 400) -> list[sqlite3.Row]:
    con = _connect()
    if con is None or not topics:
        return []
    q = _fts_query(topics)
    if not q:
        return []
    try:
        rows = con.execute(
            """SELECT a.company, a.title, a.agency, a.phase, a.program, a.award_year,
                      a.award_amount, a.state, a.city
               FROM sbir_fts f JOIN sbir_awards a ON a.id = f.rowid
               WHERE sbir_fts MATCH ?
               ORDER BY rank LIMIT ?""",
            (q, limit),
        ).fetchall()
        return rows
    except sqlite3.OperationalError:
        log.exception("FTS query failed: %s", q)
        return []
    finally:
        con.close()


def history_for_topics(topics: list[str], state: Optional[str]) -> Optional[HistoricalStats]:
    rows = similar_awards(topics, state)
    if not rows:
        return None
    amounts = [r["award_amount"] for r in rows if r["award_amount"]]
    in_state = [r for r in rows if state and r["state"] == state]
    ordered = in_state + [r for r in rows if not (state and r["state"] == state)]
    return HistoricalStats(
        similar_companies=len({r["company"] for r in rows}),
        total_awarded_usd=float(sum(amounts)),
        median_award_usd=float(statistics.median(amounts)) if amounts else 0,
        in_state_recipients=len({r["company"] for r in in_state}),
        sample_recipients=[
            {
                "name": (r["company"] or "").title(),
                "agency": _short_agency(r["agency"]),
                "amount": r["award_amount"],
                "year": r["award_year"],
                "program": f"{r['program']} {r['phase']}".strip(),
            }
            for r in ordered[:5]
        ],
    )


def _short_agency(a: str) -> str:
    return {
        "Department of Health and Human Services": "HHS",
        "National Science Foundation": "NSF",
        "Department of War": "DOW",
        "Department of Defense": "DOD",
        "National Aeronautics and Space Administration": "NASA",
        "Department of Energy": "DOE",
        "Department of Homeland Security": "DHS",
        "Environmental Protection Agency": "EPA",
        "United States Dept. of Agriculture": "USDA",
        "Department of Commerce": "DOC",
        "Department of Transportation": "DOT",
        "Department of Education": "ED",
    }.get(a, a)


def pathway_opportunities(topics: list[str], state: Optional[str], max_agencies: int = 2) -> list[Opportunity]:
    """Synthesize an 'SBIR/STTR pathway' card for the agencies that most fund this tech."""
    rows = similar_awards(topics, state)
    if not rows:
        return []
    by_agency: dict[str, list[sqlite3.Row]] = {}
    for r in rows:
        by_agency.setdefault(r["agency"], []).append(r)
    ranked = sorted(by_agency.items(), key=lambda kv: len(kv[1]), reverse=True)[:max_agencies]

    opps: list[Opportunity] = []
    for agency, ars in ranked:
        amounts = [r["award_amount"] for r in ars if r["award_amount"]]
        in_state = [r for r in ars if state and r["state"] == state]
        short = _short_agency(agency)
        ordered = in_state + [r for r in ars if not (state and r["state"] == state)]
        opps.append(
            Opportunity(
                source="sbir",
                source_id=f"sbir-{short.lower()}",
                title=f"SBIR/STTR — {short} America's Seed Fund pathway",
                agency=agency,
                program="SBIR/STTR",
                status="recurring program",
                url=AGENCY_SBIR_LINKS.get(agency, "https://www.sbir.gov/topics"),
                summary=(
                    f"{short} has made {len(ars)} SBIR/STTR awards since 2018 for technology similar "
                    f"to yours. Phase I typically ~$150K-$300K, Phase II up to ~$1M-$2M, non-dilutive."
                ),
                history=HistoricalStats(
                    similar_companies=len({r["company"] for r in ars}),
                    total_awarded_usd=float(sum(amounts)),
                    median_award_usd=float(statistics.median(amounts)) if amounts else 0,
                    in_state_recipients=len({r["company"] for r in in_state}),
                    sample_recipients=[
                        {
                            "name": (r["company"] or "").title(),
                            "agency": short,
                            "amount": r["award_amount"],
                            "year": r["award_year"],
                            "program": f"{r['program']} {r['phase']}".strip(),
                        }
                        for r in ordered[:5]
                    ],
                ),
            )
        )
    return opps
