#!/bin/bash
# AI Orchestrator Launcher
# Automatycznie aktywuje virtual environment i uruchamia MCP server

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="$SCRIPT_DIR/orchestrator_venv"

echo "🤖 Starting AI Orchestrator..."

# Check if virtual environment exists
if [ ! -d "$VENV_DIR" ]; then
    echo "❌ Virtual environment not found at $VENV_DIR"
    echo "Please run setup first: ./setup_orchestrator.sh"
    exit 1
fi

# Activate virtual environment
if [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "win32" ]]; then
    # Windows
    source "$VENV_DIR/Scripts/activate"
else
    # Unix-like systems (Linux, macOS)
    source "$VENV_DIR/bin/activate"
fi

echo "✅ Virtual environment activated"
echo "🚀 Starting MCP server..."

# Run MCP server
bash "$SCRIPT_DIR/.cursor/orchestrator/start_mcp_server.sh"

# Deactivate when done
deactivate
echo "👋 Orchestrator stopped"
