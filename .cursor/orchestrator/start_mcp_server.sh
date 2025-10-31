#!/bin/bash
# Start MCP Server for AI Orchestrator - SILENT MODE
# This script starts the MCP server using stdio transport
# NO OUTPUT ALLOWED - MCP uses stdin/stdout for JSON communication

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

# Set Python path to include the orchestrator module
export PYTHONPATH="$PROJECT_ROOT/.cursor:$PYTHONPATH"

# Change to the orchestrator directory
cd "$SCRIPT_DIR"

# Start the MCP server (completely silent - no output)
exec python -m orchestrator.mcp_server
