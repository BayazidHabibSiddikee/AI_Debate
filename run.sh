#!/bin/bash
# AI Debate Simulator — Start Script
# Usage:
#   ./run.sh          — start
#   ./run.sh stop     — stop the simulator

VENV="$HOME/marin_venv"
PORT=5050
PID_FILE="./simulator.pid"

stop_simulator() {
    echo "🛑 Stopping Debate Simulator..."
    if [ -f "$PID_FILE" ]; then
        SPID=$(cat "$PID_FILE")
        if kill -0 "$SPID" 2>/dev/null; then
            kill "$SPID"
            echo "   ✓ Process $SPID stopped."
        fi
        rm -f "$PID_FILE"
    fi

    # Fallback to kill by port
    PID=$(ss -tlnp "sport = :$PORT" 2>/dev/null | grep -oP 'pid=\K[0-9]+' | head -1)
    if [ -n "$PID" ]; then
        kill "$PID" 2>/dev/null && echo "   ✓ Killed process $PID on port $PORT."
    fi
    echo "✅ Simulator is offline."
}

start_simulator() {
    echo "🏹 Starting Debate Simulator using Marin's venv..."
    
    if [ ! -d "$VENV" ]; then
        echo "❌ Virtual environment not found at $VENV"
        exit 1
    fi
    
    source "$VENV/bin/activate"
    
    # Run the app in background
    nohup python3 app.py > simulator.log 2>&1 &
    PID=$!
    echo $PID > "$PID_FILE"
    
    echo "⏳ Waiting for service to start..."
    for i in $(seq 1 10); do
        if ss -tlnp 2>/dev/null | grep -q ":$PORT"; then
            echo "✨ Debate Simulator is online!"
            echo "🌍 Portal: http://localhost:$PORT"
            echo "------------------------------------------------"
            echo "Run './run.sh stop' to shut it down."
            exit 0
        fi
        sleep 1
    done
    echo "⚠️  App took longer than expected or failed to start. Check simulator.log"
}

case "${1:-start}" in
    stop)    stop_simulator ;;
    restart) stop_simulator; sleep 1; start_simulator ;;
    start|"") start_simulator ;;
    *)
        echo "Usage: $0 [start|stop|restart]"
        exit 1
        ;;
esac
