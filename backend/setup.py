"""Cross-platform setup for Server 1 (GovMatch backend): macOS, Linux, Windows.

    uv run python setup.py            # everything
    uv run python setup.py --no-llm   # skip the local LLM model (embeddings-only matching)

Idempotent: safe to re-run; skips what's already done. Needs: uv, and either Docker
(recommended, any OS) or a local mongod on :27017.
"""
from __future__ import annotations

import argparse
import os
import platform
import shutil
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
CSV = HERE / "data" / "raw" / "sbir_award_data.csv"
CSV_URL = "https://data.www.sbir.gov/awarddatapublic/award_data.csv"
MONGO_URL = os.environ.get("MONGO_URL", "mongodb://localhost:27017")
IS_APPLE_SILICON = platform.system() == "Darwin" and platform.machine() == "arm64"


def step(msg: str) -> None:
    print(f"\n\033[1m▸ {msg}\033[0m", flush=True)


def run(cmd: list[str], **kw) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, text=True, **kw)


def mongo_ok() -> bool:
    try:
        from pymongo import MongoClient

        MongoClient(MONGO_URL, serverSelectionTimeoutMS=1500).admin.command("ping")
        return True
    except Exception:
        return False


def ensure_mongo() -> None:
    step("MongoDB")
    if mongo_ok():
        print(f"reachable at {MONGO_URL}")
        return
    if shutil.which("docker"):
        print("starting MongoDB via Docker Compose…")
        run(["docker", "compose", "up", "-d", "mongo"], cwd=ROOT)
        for _ in range(40):
            if mongo_ok():
                print("mongod running (docker)")
                return
            time.sleep(1.5)
    if platform.system() == "Darwin" and shutil.which("brew"):
        print("Docker not available — installing MongoDB via Homebrew…")
        run(["brew", "tap", "mongodb/brew"], capture_output=True)
        run(["brew", "trust", "mongodb/brew"], capture_output=True)
        run(["brew", "install", "mongodb-community"])
        run(["brew", "services", "start", "mongodb/brew/mongodb-community"])
        for _ in range(20):
            if mongo_ok():
                print("mongod running (brew)")
                return
            time.sleep(1)
    sys.exit(
        "\nMongoDB is not reachable. Easiest fix on any OS: install Docker Desktop, then re-run.\n"
        "Or install MongoDB Community and start it on :27017 (see mongodb.com/docs/manual/installation)."
    )


def ensure_sbir_csv() -> None:
    step("SBIR bulk award data (~350MB, one-time download)")
    CSV.parent.mkdir(parents=True, exist_ok=True)
    if CSV.exists() and CSV.stat().st_size > 100_000_000:
        print("already downloaded")
        return
    req = urllib.request.Request(CSV_URL, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=60) as r, open(CSV, "wb") as f:
        total = int(r.headers.get("Content-Length") or 0)
        done = 0
        while chunk := r.read(1 << 20):
            f.write(chunk)
            done += len(chunk)
            if total:
                print(f"\r  {done * 100 // total:3d}%", end="", flush=True)
    print("\r  100% ✓")


def sbir_loaded() -> bool:
    try:
        from pymongo import MongoClient

        return MongoClient(MONGO_URL).govmatch.sbir_awards.estimated_document_count() > 30_000
    except Exception:
        return False


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-llm", action="store_true", help="skip local LLM model download")
    args = ap.parse_args()

    print(f"GovMatch Server 1 setup — {platform.system()} {platform.machine()}")

    step("Python dependencies")
    run(["uv", "sync"], cwd=HERE, check=True)

    ensure_mongo()
    ensure_sbir_csv()

    step("Load SBIR awards into MongoDB (39.8K rows, ~1 min)")
    if sbir_loaded():
        print("already loaded")
    else:
        run(["uv", "run", "python", "-m", "app.ingest.sbir_ingest", "2018"], cwd=HERE, check=True)

    step("Harvest Grants.gov opportunities into the warehouse (~900 programs, ~20s, needs internet)")
    r = run(["uv", "run", "python", "-m", "app.ingest.harvest"], cwd=HERE, capture_output=True)
    print((r.stdout or "").strip().splitlines()[-1] if r.stdout else (r.stderr or "").strip()[-300:])

    step("Embedding model (bge-small, ~130MB, one-time)")
    run(["uv", "run", "python", "-c", "from app.services import embeddings; embeddings.warmup(); print('ready')"], cwd=HERE)

    step("Local LLM relevance judge")
    if args.no_llm:
        print("skipped (--no-llm) — matching runs on embeddings + rules")
    elif IS_APPLE_SILICON:
        print("Apple Silicon → MLX (Qwen3-4B, ~2.5GB, one-time)…")
        run(["uv", "run", "python", "-c",
             "from mlx_lm import load; load('mlx-community/Qwen3-4B-4bit'); print('MLX model ready')"], cwd=HERE)
    else:
        if shutil.which("ollama"):
            print("Ollama found → pulling qwen3:4b (~2.5GB, one-time)…")
            run(["ollama", "pull", "qwen3:4b"])
        else:
            print(
                "No MLX on this platform. For the LLM judge, install Ollama (https://ollama.com), then:\n"
                "    ollama pull qwen3:4b\n"
                "Without it, matching still works on embeddings + rules (the 'Analyst' line is absent)."
            )

    print("\n\033[32m✓ Setup complete.\033[0m\n")
    print("Start Server 1:   cd backend && uv run uvicorn app.main:app --port 8000")
    print("Health:           curl localhost:8000/api/health")
    print("GraphQL explorer: http://localhost:8000/graphql")


if __name__ == "__main__":
    main()
