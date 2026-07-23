#!/bin/bash
# AI Debate Simulator — Start Script
# Usage:
#   ./run.sh          — start
#   ./run.sh stop     — stop the simulator

VENV="$HOME/marin_venv"
DEBATE_PORT=5050
RAG_PORT=5080
PID_FILE="./simulator.pid"
RAG_PID_FILE="./rag.pid"

stop_simulator() {
    echo "🛑 Stopping Debate Simulator & RAG..."
    
    if [ -f "$PID_FILE" ]; then
        kill "$(cat "$PID_FILE")" 2>/dev/null
        rm -f "$PID_FILE"
    fi
    
    if [ -f "$RAG_PID_FILE" ]; then
        kill "$(cat "$RAG_PID_FILE")" 2>/dev/null
        rm -f "$RAG_PID_FILE"
    fi

    # Fallback kills
    for PORT in $DEBATE_PORT $RAG_PORT; do
        PID=$(ss -tlnp "sport = :$PORT" 2>/dev/null | grep -oP 'pid=\K[0-9]+' | head -1)
        if [ -n "$PID" ]; then
            kill "$PID" 2>/dev/null && echo "   ✓ Killed process $PID on port $PORT."
        fi
    done
    echo "✅ Platform is offline."
}

start_simulator() {
    echo "🏹 Starting Nexus Debate Platform..."
    
    if [ ! -d "$VENV" ]; then
        echo "❌ Virtual environment not found at $VENV"
        exit 1
    fi
    
    source "$VENV/bin/activate"
    
    # Run RAG Server
    echo "📚 Starting RAG Engine..."
    nohup python3 rag_server.py --port $RAG_PORT > rag.log 2>&1 &
    echo $! > "$RAG_PID_FILE"
    
    # Run Debate App
    echo "💬 Starting Debate App..."
    nohup python3 app.py > simulator.log 2>&1 &
    echo $! > "$PID_FILE"
    
    echo "⏳ Waiting for services to ascend..."
    for i in $(seq 1 15); do
        if ss -tlnp 2>/dev/null | grep -q ":$DEBATE_PORT"; then
            echo "✨ Nexus Debate Platform is online!"
            echo "🌍 Portal:        http://localhost:$DEBATE_PORT"
            echo "📚 RAG Endpoint:  http://localhost:$RAG_PORT"
            echo "------------------------------------------------"
            echo "Run './run.sh stop' to shut it down."
            exit 0
        fi
        sleep 1
    done
    echo "⚠️  App took longer than expected. Check simulator.log and rag.log"
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
