#!/usr/bin/env bash
# One-command health check for the whole stack. Run before any demo.
#   bash scripts/check_stack.sh
# Exit code 0 = everything wired; anything else = read the red lines.
S1="${GOVMATCH_URL:-http://localhost:8000}"
S2="${SERVER2_URL:-http://localhost:8002}"
FE="${FRONTEND_URL:-http://localhost:5174}"
ok=0; bad=0
pass() { printf '  \033[32m✓\033[0m %s\n' "$1"; ok=$((ok+1)); }
fail() { printf '  \033[31m✗\033[0m %s\n' "$1"; bad=$((bad+1)); }

echo "MongoDB"
if mongosh --quiet --eval 'db.getSiblingDB("govmatch").opportunities.countDocuments()' >/tmp/_n 2>/dev/null; then
  pass "reachable · $(cat /tmp/_n) opportunities in warehouse"
else fail "mongod not reachable — brew services start mongodb/brew/mongodb-community"; fi

echo "Server 1 (GovMatch backend, $S1)"
H=$(curl -s -m 4 "$S1/api/health" 2>/dev/null)
if [ -n "$H" ]; then
  pass "up · $(echo "$H" | python3 -c 'import json,sys; d=json.load(sys.stdin); print("judge="+d.get("relevance_judge","?"))')"
  echo "$H" | grep -q '"mlx:' && pass "local LLM judge active (MLX)" || fail "LLM judge not on MLX — check backend log"
else fail "not responding — bash backend/scripts/install_service.sh status"; fi

echo "Server 2 (matcher, $S2)"
H2=$(curl -s -m 4 "$S2/health" 2>/dev/null)
if [ -n "$H2" ]; then
  if echo "$H2" | grep -q "GovMatch Server 1"; then pass "up · wired to Server 1 (live data)"
  else fail "up but serving MOCK data — Server 1 unreachable from Server 2"; fi
else fail "not responding — cd server2 && uvicorn app.main:app --port 8002"; fi

echo "Frontend ($FE)"
if curl -s -m 4 -o /dev/null -w '%{http_code}' "$FE" 2>/dev/null | grep -q 200; then pass "up"
else fail "not responding — cd frontend && npm run dev -- --port 5174"; fi

echo "Nightly harvester"
if launchctl print "gui/$(id -u)/com.govmatch.harvest" >/dev/null 2>&1; then
  pass "installed · $(launchctl print "gui/$(id -u)/com.govmatch.harvest" | grep 'last exit code' | xargs)"
else fail "not installed — bash backend/scripts/install_nightly.sh"; fi

echo
if [ "$bad" -eq 0 ]; then printf '\033[32mAll %d checks passed — demo ready.\033[0m\n' "$ok"; exit 0
else printf '\033[31m%d problem(s).\033[0m\n' "$bad"; exit 1; fi
