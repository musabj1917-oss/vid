#!/usr/bin/env bash
# Daemon controller for autonomous video scheduler
set -e

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PID_FILE="$DIR/.pipeline/scheduler.pid"
LOG_FILE="$DIR/.pipeline/scheduler.log"

mkdir -p "$DIR/.pipeline"

case "$1" in
    start)
        if [ -f "$PID_FILE" ] && kill -0 "$(cat "$PID_FILE")" 2>/dev/null; then
            echo "Scheduler daemon is already running (PID: $(cat "$PID_FILE"))."
            exit 0
        fi
        echo "Starting video scheduler daemon in background..."
        nohup node "$DIR/scheduler.js" >> "$LOG_FILE" 2>&1 &
        echo $! > "$PID_FILE"
        echo "✅ Scheduler started with PID $(cat "$PID_FILE"). Logs at $LOG_FILE"
        ;;
    stop)
        if [ -f "$PID_FILE" ]; then
            PID="$(cat "$PID_FILE")"
            if kill -0 "$PID" 2>/dev/null; then
                kill "$PID"
                echo "Stopped scheduler daemon (PID: $PID)."
            else
                echo "Process $PID not running. Cleaning up PID file."
            fi
            rm -f "$PID_FILE"
        else
            echo "No PID file found. Scheduler daemon is not running."
        fi
        ;;
    status)
        if [ -f "$PID_FILE" ] && kill -0 "$(cat "$PID_FILE")" 2>/dev/null; then
            echo "✅ Scheduler daemon is running (PID: $(cat "$PID_FILE"))."
        else
            echo "⚪ Scheduler daemon is NOT running."
        fi
        ;;
    logs)
        tail -n 30 -f "$LOG_FILE"
        ;;
    *)
        echo "Usage: $0 {start|stop|status|logs}"
        exit 1
        ;;
esac
