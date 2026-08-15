#!/usr/bin/env bash
# Run the GovMatch backend (Server 1) as a macOS launchd service: starts at login,
# restarts if it dies, logs to backend/data/logs/. No more ad-hoc nohup processes.
#   bash scripts/install_service.sh            # install + start
#   bash scripts/install_service.sh restart    # restart (after code changes)
#   bash scripts/install_service.sh status     # is it up? which judge? which port?
#   bash scripts/install_service.sh logs       # tail the log
#   bash scripts/install_service.sh uninstall
set -euo pipefail

LABEL="com.govmatch.server1"
BACKEND_DIR="$(cd "$(dirname "$0")/.." && pwd)"
PLIST="$HOME/Library/LaunchAgents/$LABEL.plist"
LOG_DIR="$BACKEND_DIR/data/logs"
UV_BIN="$(command -v uv)"
PORT="${GOVMATCH_PORT:-8000}"

status() {
  printf 'launchd: '
  launchctl print "gui/$(id -u)/$LABEL" 2>/dev/null | grep -E "state = " | xargs || echo "not installed"
  printf 'health:  '
  curl -s -m 3 "http://localhost:$PORT/api/health" || echo "no response on :$PORT (starting? MLX load takes ~30s)"
  echo
}

case "${1:-install}" in
  status) status; exit 0 ;;
  logs) tail -n 40 -f "$LOG_DIR/backend.log" ;;
  restart)
    launchctl kickstart -k "gui/$(id -u)/$LABEL"
    echo "restarting $LABEL — MLX model load takes ~30s"; sleep 8; status; exit 0 ;;
  uninstall)
    launchctl bootout "gui/$(id -u)/$LABEL" 2>/dev/null || true
    rm -f "$PLIST"; echo "removed $LABEL"; exit 0 ;;
esac

# stop any ad-hoc uvicorn on the port so the service owns it
lsof -ti ":$PORT" | xargs kill 2>/dev/null || true

mkdir -p "$LOG_DIR" "$HOME/Library/LaunchAgents"
cat > "$PLIST" <<EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0"><dict>
  <key>Label</key><string>$LABEL</string>
  <key>ProgramArguments</key><array>
    <string>/bin/bash</string><string>$BACKEND_DIR/scripts/run_server.sh</string>
  </array>
  <key>WorkingDirectory</key><string>$BACKEND_DIR</string>
  <key>RunAtLoad</key><true/>
  <key>StartInterval</key><integer>60</integer>
  <key>StandardOutPath</key><string>$LOG_DIR/backend.log</string>
  <key>StandardErrorPath</key><string>$LOG_DIR/backend.err.log</string>
  <key>EnvironmentVariables</key><dict>
    <key>PATH</key><string>/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin</string>
    <key>HOME</key><string>$HOME</string>
    <key>GOVMATCH_PORT</key><string>$PORT</string>
  </dict>
</dict></plist>
EOF

launchctl bootout "gui/$(id -u)/$LABEL" 2>/dev/null || true
launchctl bootstrap "gui/$(id -u)" "$PLIST"
echo "installed $LABEL — starts at login, restarts on crash, port $PORT, logs in $LOG_DIR"
echo "waiting for MLX model load…"
for i in $(seq 1 40); do
  sleep 3
  if curl -s -m 2 "http://localhost:$PORT/api/health" >/dev/null 2>&1; then break; fi
done
status
