#!/bin/bash
# Start MCP Server for AI Orchestrator - SILENT MODE
# This script starts the MCP server using stdio transport
# NO OUTPUT ALLOWED - MCP uses stdin/stdout for JSON communication

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
VENV_DIR="$PROJECT_ROOT/orchestrator_venv"

# Check if virtual environment exists
if [ ! -d "$VENV_DIR" ]; then
    echo "Virtual environment not found at $VENV_DIR"
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

# Set Python path to include the orchestrator module
export PYTHONPATH="$PROJECT_ROOT/.cursor:$PYTHONPATH"

# Change to the orchestrator directory
cd "$SCRIPT_DIR"

# Start the MCP server (completely silent - no output)
exec python -m orchestrator.mcp_server
