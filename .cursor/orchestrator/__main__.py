#!/usr/bin/env python3
"""
Main entry point for MCP Orchestrator Server
Allows running as: python -m orchestrator
"""

import asyncio
from .mcp_server import start_mcp_server

if __name__ == "__main__":
    asyncio.run(start_mcp_server())
