#!/usr/bin/env bash
# Fresh-machine setup for Server 1 (GovMatch backend). macOS. Idempotent — safe to re-run.
#   bash backend/scripts/setup.sh
# Afterwards:  cd backend && uv run uvicorn app.main:app --port 8000
set -euo pipefail
cd "$(dirname "$0")/.."

step() { printf '\n\033[1m▸ %s\033[0m\n' "$1"; }
have() { command -v "$1" >/dev/null 2>&1; }

step "Homebrew"
have brew || { echo "Install Homebrew first: https://brew.sh"; exit 1; }

step "uv (Python package manager)"
have uv || brew install uv

step "MongoDB (local, no auth)"
if ! have mongod; then
  brew tap mongodb/brew >/dev/null 2>&1 || true
  brew trust mongodb/brew >/dev/null 2>&1 || true
  brew install mongodb-community
fi
brew services start mongodb/brew/mongodb-community >/dev/null 2>&1 || true
for i in $(seq 1 15); do mongosh --quiet --eval 'db.runCommand({ping:1}).ok' >/dev/null 2>&1 && break; sleep 1; done
mongosh --quiet --eval 'db.runCommand({ping:1}).ok' >/dev/null 2>&1 && echo "mongod running" || { echo "mongod not responding — run: brew services start mongodb/brew/mongodb-community"; exit 1; }

step "Python deps (uv sync)"
uv sync

step "SBIR bulk award data (~350MB, one-time download from data.www.sbir.gov)"
mkdir -p data/raw
if [ ! -s data/raw/sbir_award_data.csv ]; then
  curl -L --progress-bar -o data/raw/sbir_award_data.csv \
    -H 'User-Agent: Mozilla/5.0' "https://data.www.sbir.gov/awarddatapublic/award_data.csv"
else echo "already downloaded"; fi

step "Load SBIR awards into MongoDB (39.8K rows, ~1 min)"
if [ "$(mongosh --quiet --eval 'db.getSiblingDB("govmatch").sbir_awards.countDocuments()')" -gt 30000 ] 2>/dev/null; then
  echo "already loaded"
else uv run python -m app.ingest.sbir_ingest 2018; fi

step "Harvest Grants.gov opportunities into the warehouse (~900 programs, ~20s)"
uv run python -m app.ingest.harvest | tail -3

step "Local LLM model (Qwen3-4B, ~2.5GB, one-time; Apple Silicon via MLX)"
if [ "$(uname -m)" = "arm64" ]; then
  uv run python -c "from mlx_lm import load; load('mlx-community/Qwen3-4B-4bit'); print('MLX model ready')" 2>&1 | grep -v "Fetching\|it/s" | tail -1
else
  echo "not Apple Silicon — MLX skipped. Optional Ollama fallback: brew install ollama && brew services start ollama && ollama pull qwen3:4b"
  echo "(without either, matching still works on embeddings + rules)"
fi

step "Embedding model (bge-small, ~130MB, one-time)"
uv run python -c "from app.services import embeddings; embeddings.warmup(); print('embeddings ready')" 2>&1 | grep -v "Fetching\|it/s\|Warning" | tail -1

step "Nightly harvester at 00:00 (launchd) — optional"
bash scripts/install_nightly.sh >/dev/null 2>&1 && echo "installed" || echo "skipped"

printf '\n\033[32m✓ Setup complete.\033[0m\n\n'
echo "Start Server 1:"
echo "  cd backend && uv run uvicorn app.main:app --port 8000"
echo "  (or as a self-restarting service: bash scripts/install_service.sh)"
echo "Then: curl localhost:8000/api/health   → GraphQL at http://localhost:8000/graphql"
echo "Whole-stack check: bash ../scripts/check_stack.sh"
