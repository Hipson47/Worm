#!/usr/bin/env python3
"""
MCP Orchestrator Client - For Cursor Agent Integration
Simplified client for calling MCP orchestrator tools
"""

import asyncio
import json
import logging
import sys
from typing import Dict, Any, Optional, List
from pathlib import Path

from mcp_server import MCPOrchestratorServer

logger = logging.getLogger(__name__)

class MCPOrchestratorClient:
    """Client for MCP Orchestrator tools"""

    def __init__(self):
        self.server = MCPOrchestratorServer()

    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Call an MCP tool"""
        try:
            # Simulate MCP tool call
            result = await self._execute_tool(tool_name, arguments)
            return result
        except Exception as e:
            logger.error(f"Error calling MCP tool {tool_name}: {e}")
            return {"error": str(e)}

    async def _execute_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Execute tool logic"""
        if tool_name == "orchestrate_task":
            return await self.server._handle_orchestrate_task(arguments)
        elif tool_name == "select_rules":
            return await self.server._handle_select_rules(arguments)
        elif tool_name == "get_execution_plan":
            return await self.server._handle_get_execution_plan(arguments)
        elif tool_name == "query_knowledge":
            return await self.server._handle_query_knowledge(arguments)
        elif tool_name == "analyze_code":
            return await self.server._handle_analyze_code(arguments)
        else:
            raise ValueError(f"Unknown tool: {tool_name}")

# Convenience functions for rules
async def call_mcp_tool(tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
    """Call MCP tool"""
    client = MCPOrchestratorClient()
    return await client.call_tool(tool_name, arguments)

async def select_optimal_rules_mcp(task_description: str, current_file: str = None,
                                 project_type: str = None) -> List[str]:
    """Select optimal rules using MCP orchestrator"""
    arguments = {
        "task_description": task_description,
        "current_file": current_file,
        "project_type": project_type
    }

    result = await call_mcp_tool("select_rules", arguments)
    return result.get("rules", [])

async def get_execution_plan_mcp(task_description: str) -> Dict[str, Any]:
    """Get execution plan using MCP orchestrator"""
    arguments = {"task": task_description}

    result = await call_mcp_tool("get_execution_plan", arguments)
    return result.get("plan", {})

async def analyze_code_with_mcp(code: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
    """Analyze code using MCP orchestrator"""
    arguments = {
        "code": code,
        "context": context or {}
    }

    result = await call_mcp_tool("analyze_code", arguments)
    return result

async def query_knowledge_mcp(query: str, context: str = None) -> str:
    """Query knowledge base using MCP orchestrator"""
    arguments = {
        "query": query,
        "context": context
    }

    result = await call_mcp_tool("query_knowledge", arguments)
    return result.get("response", "")

# Synchronous wrapper for rules that don't support async
def select_optimal_rules_sync(task_description: str, current_file: str = None,
                            project_type: str = None) -> List[str]:
    """Synchronous wrapper for select_optimal_rules_mcp"""
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            # If loop is already running, use it
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(asyncio.run, select_optimal_rules_mcp(
                    task_description, current_file, project_type))
                return future.result()
        else:
            return loop.run_until_complete(select_optimal_rules_mcp(
                task_description, current_file, project_type))
    except Exception as e:
        logger.error(f"Error in sync wrapper: {e}")
        return ["30_hybrid_moe_tot_reasoning", "31_advanced_agent_steering"]  # fallback

def get_execution_plan_sync(task_description: str) -> Dict[str, Any]:
    """Synchronous wrapper for get_execution_plan_mcp"""
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(asyncio.run, get_execution_plan_mcp(task_description))
                return future.result()
        else:
            return loop.run_until_complete(get_execution_plan_mcp(task_description))
    except Exception as e:
        logger.error(f"Error in sync wrapper: {e}")
        return {"error": "Failed to get execution plan"}

def analyze_code_sync(code: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
    """Synchronous wrapper for analyze_code_with_mcp"""
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(asyncio.run, analyze_code_with_mcp(code, context))
                return future.result()
        else:
            return loop.run_until_complete(analyze_code_with_mcp(code, context))
    except Exception as e:
        logger.error(f"Error in sync wrapper: {e}")
        return {"error": "Failed to analyze code"}

def query_knowledge_sync(query: str, context: str = None) -> str:
    """Synchronous wrapper for query_knowledge_mcp"""
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(asyncio.run, query_knowledge_mcp(query, context))
                return future.result()
        else:
            return loop.run_until_complete(query_knowledge_mcp(query, context))
    except Exception as e:
        logger.error(f"Error in sync wrapper: {e}")
        return "Knowledge query failed"
