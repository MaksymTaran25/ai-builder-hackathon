"""Load the SBIR.gov bulk award CSV into MongoDB with a weighted text index.

Usage: uv run python -m app.ingest.sbir_ingest [min_year]
Source file: data/raw/sbir_award_data.csv (from data.www.sbir.gov)
Target: mongodb://localhost:27017 (override with MONGO_URL), db govmatch.
"""
from __future__ import annotations

import csv
import os
import sys
from pathlib import Path

from pymongo import ASCENDING, TEXT, MongoClient

CSV_PATH = Path(__file__).resolve().parents[2] / "data" / "raw" / "sbir_award_data.csv"
MONGO_URL = os.environ.get("MONGO_URL", "mongodb://localhost:27017")


def _num(s: str) -> float:
    try:
        return float(s.replace(",", "").replace("$", "") or 0)
    except ValueError:
        return 0


def main(min_year: int = 2018) -> None:
    csv.field_size_limit(10_000_000)
    client = MongoClient(MONGO_URL)
    col = client.govmatch.sbir_awards
    col.drop()

    n = 0
    with open(CSV_PATH, encoding="utf-8", errors="replace", newline="") as f:
        reader = csv.reader(f)
        next(reader)  # header
        batch = []
        for row in reader:
            if len(row) < 30:
                continue
            try:
                year = int(row[16] or 0)
            except ValueError:
                continue
            if year < min_year:
                continue
            batch.append({
                "company": row[0], "title": row[1], "agency": row[2], "branch": row[3],
                "phase": row[4], "program": row[5], "topic_code": row[15],
                "award_year": year, "award_amount": _num(row[17]),
                "employees": int(_num(row[22])), "city": row[26], "state": row[27],
                "abstract": row[29],
            })
            if len(batch) >= 5000:
                col.insert_many(batch); n += len(batch); batch = []
        if batch:
            col.insert_many(batch); n += len(batch)

    col.create_index(
        [("title", TEXT), ("abstract", TEXT), ("company", TEXT)],
        weights={"title": 4, "abstract": 2, "company": 1},
        name="sbir_text",
    )
    col.create_index([("state", ASCENDING)])
    col.create_index([("agency", ASCENDING), ("award_year", ASCENDING)])

    print(f"ingested {n} awards (year >= {min_year}) into {MONGO_URL} govmatch.sbir_awards")
    for row in col.aggregate([
        {"$group": {"_id": "$state", "c": {"$sum": 1}}},
        {"$sort": {"c": -1}}, {"$limit": 5},
    ]):
        print("  ", (row["_id"], row["c"]))
    client.close()


if __name__ == "__main__":
    main(int(sys.argv[1]) if len(sys.argv) > 1 else 2018)
