"""Load the SBIR.gov bulk award CSV into SQLite with an FTS5 index.

Usage: uv run python -m app.ingest.sbir_ingest [min_year]
Source file: data/raw/sbir_award_data.csv (from data.www.sbir.gov)
"""
from __future__ import annotations

import csv
import sqlite3
import sys
from pathlib import Path

DB_PATH = Path(__file__).resolve().parents[2] / "data" / "gov.db"
CSV_PATH = Path(__file__).resolve().parents[2] / "data" / "raw" / "sbir_award_data.csv"

SCHEMA = """
DROP TABLE IF EXISTS sbir_awards;
CREATE TABLE sbir_awards (
    id INTEGER PRIMARY KEY,
    company TEXT, title TEXT, agency TEXT, branch TEXT, phase TEXT, program TEXT,
    topic_code TEXT, award_year INTEGER, award_amount REAL,
    employees INTEGER, city TEXT, state TEXT, abstract TEXT
);
DROP TABLE IF EXISTS sbir_fts;
CREATE VIRTUAL TABLE sbir_fts USING fts5(
    title, abstract, company, content='sbir_awards', content_rowid='id'
);
"""


def _num(s: str) -> float:
    try:
        return float(s.replace(",", "").replace("$", "") or 0)
    except ValueError:
        return 0


def main(min_year: int = 2018) -> None:
    csv.field_size_limit(10_000_000)
    con = sqlite3.connect(DB_PATH)
    con.executescript(SCHEMA)
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
            batch.append((
                row[0], row[1], row[2], row[3], row[4], row[5], row[15],
                year, _num(row[17]), int(_num(row[22])), row[26], row[27], row[29],
            ))
            if len(batch) >= 5000:
                _flush(con, batch); n += len(batch); batch = []
        if batch:
            _flush(con, batch); n += len(batch)
    con.execute("INSERT INTO sbir_fts(rowid, title, abstract, company) SELECT id, title, abstract, company FROM sbir_awards")
    con.commit()
    print(f"ingested {n} awards (year >= {min_year}) into {DB_PATH}")
    for row in con.execute("SELECT state, COUNT(*) c FROM sbir_awards GROUP BY state ORDER BY c DESC LIMIT 5"):
        print("  ", row)
    con.close()


def _flush(con: sqlite3.Connection, batch: list) -> None:
    con.executemany(
        "INSERT INTO sbir_awards (company,title,agency,branch,phase,program,topic_code,award_year,award_amount,employees,city,state,abstract) "
        "VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)",
        batch,
    )


if __name__ == "__main__":
    main(int(sys.argv[1]) if len(sys.argv) > 1 else 2018)
