#!/bin/bash
# Watchdog: start Server 1 if it isn't listening. launchd runs this every minute
# (StartInterval), which achieves KeepAlive semantics without KeepAlive.
cd "$(dirname "$0")/.." || exit 1
export PATH="/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin"
PORT="${GOVMATCH_PORT:-8000}"
if curl -s -m 3 "http://localhost:$PORT/api/health" >/dev/null 2>&1; then exit 0; fi
if lsof -ti ":$PORT" >/dev/null 2>&1; then exit 0; fi   # starting up (MLX load)
echo "$(date '+%Y-%m-%d %H:%M:%S') watchdog: starting server on :$PORT" >> data/logs/backend.log
nohup uv run uvicorn app.main:app --host 0.0.0.0 --port "$PORT" >> data/logs/backend.log 2>&1 &
exit 0
