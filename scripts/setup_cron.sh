#!/usr/bin/env bash
# Setup automated cron schedule for vidagents
set -e

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CRON_FILE="$DIR/crontab.txt"

if command -v crontab >/dev/null 2>&1; then
    echo "Registering crontab from $CRON_FILE..."
    crontab "$CRON_FILE"
    echo "✅ Crontab successfully installed:"
    crontab -l
else
    echo "⚠️ 'crontab' command not found in current environment."
    echo "You can run the built-in Node scheduler daemon instead:"
    echo "  npm run schedule"
    echo "or:"
    echo "  ./scripts/daemon_ctl.sh start"
fi
