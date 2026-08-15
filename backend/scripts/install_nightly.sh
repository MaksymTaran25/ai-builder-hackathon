#!/usr/bin/env bash
# Install (or reinstall) the nightly harvester as a macOS launchd job: runs at 00:00
# every day, survives reboots, catches up if the Mac was asleep at midnight.
#   bash scripts/install_nightly.sh            # install
#   bash scripts/install_nightly.sh uninstall  # remove
#   bash scripts/install_nightly.sh run-now    # trigger immediately (test)
set -euo pipefail

LABEL="com.govmatch.harvest"
BACKEND_DIR="$(cd "$(dirname "$0")/.." && pwd)"
PLIST="$HOME/Library/LaunchAgents/$LABEL.plist"
LOG_DIR="$BACKEND_DIR/data/logs"
UV_BIN="$(command -v uv)"

case "${1:-install}" in
  uninstall)
    launchctl bootout "gui/$(id -u)/$LABEL" 2>/dev/null || true
    rm -f "$PLIST"
    echo "removed $LABEL"
    exit 0 ;;
  run-now)
    launchctl kickstart -k "gui/$(id -u)/$LABEL"
    echo "kicked $LABEL — tail $LOG_DIR/harvest.log"
    exit 0 ;;
esac

mkdir -p "$LOG_DIR" "$HOME/Library/LaunchAgents"
cat > "$PLIST" <<EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0"><dict>
  <key>Label</key><string>$LABEL</string>
  <key>ProgramArguments</key><array>
    <string>$UV_BIN</string><string>run</string><string>python</string>
    <string>-m</string><string>app.ingest.harvest</string>
  </array>
  <key>WorkingDirectory</key><string>$BACKEND_DIR</string>
  <key>StartCalendarInterval</key><dict><key>Hour</key><integer>0</integer><key>Minute</key><integer>0</integer></dict>
  <key>StandardOutPath</key><string>$LOG_DIR/harvest.log</string>
  <key>StandardErrorPath</key><string>$LOG_DIR/harvest.err.log</string>
  <key>EnvironmentVariables</key><dict>
    <key>PATH</key><string>/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin</string>
    <key>HOME</key><string>$HOME</string>
  </dict>
</dict></plist>
EOF

launchctl bootout "gui/$(id -u)/$LABEL" 2>/dev/null || true
launchctl bootstrap "gui/$(id -u)" "$PLIST"
echo "installed $LABEL — runs daily at 00:00; logs in $LOG_DIR"
launchctl print "gui/$(id -u)/$LABEL" | grep -E "state|last exit" | head -3 || true
