#!/usr/bin/env python3
"""
AI Orchestrator Client - For Cursor Agent Integration
Module for the Cursor agent to communicate with the AI Orchestrator Service
Supports both HTTP API and MCP (Model Context Protocol) transports
"""

import asyncio
import json
import logging
import subprocess
import sys
from typing import Dict, Any, Optional, List
from pathlib import Path
from dataclasses import dataclass

try:
    import aiohttp
    AIOHTTP_AVAILABLE = True
except ImportError:
    AIOHTTP_AVAILABLE = False
    import requests

logger = logging.getLogger(__name__)

@dataclass
class MCPToolResult:
    """Result from MCP tool call"""
    content: List[Dict[str, Any]]
    is_error: bool = False

class MCPClient:
    """MCP Client for communicating with MCP servers via stdio"""

    def __init__(self, server_command: List[str]):
        self.server_command = server_command
        self.process = None
        self.initialized = False

    async def start_server(self):
        """Start MCP server process"""
        try:
            self.process = await asyncio.create_subprocess_exec(
                *self.server_command,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            logger.info(f"Started MCP server: {' '.join(self.server_command)}")
            return True
        except Exception as e:
            logger.error(f"Failed to start MCP server: {e}")
            return False

    async def stop_server(self):
        """Stop MCP server process"""
        if self.process:
            try:
                self.process.terminate()
                await asyncio.wait_for(self.process.wait(), timeout=5.0)
                logger.info("MCP server stopped")
            except Exception as e:
                logger.warning(f"Error stopping MCP server: {e}")
                self.process.kill()

    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> MCPToolResult:
        """Call MCP tool"""
        if not self.process:
            return MCPToolResult(content=[], is_error=True)

        # Prepare request
        request = {
            "jsonrpc": "2.0",
            "id": f"call_{tool_name}_{asyncio.get_event_loop().time()}",
            "method": "tools/call",
            "params": {
                "name": tool_name,
                "arguments": arguments
            }
        }

        try:
            # Send request
            request_json = json.dumps(request).encode() + b'\n'
            self.process.stdin.write(request_json)
            await self.process.stdin.drain()

            # Read response
            response_line = await self.process.stdout.readline()
            if not response_line:
                return MCPToolResult(content=[], is_error=True)

            response = json.loads(response_line.decode().strip())

            if "error" in response:
                logger.error(f"MCP tool error: {response['error']}")
                return MCPToolResult(
                    content=[{"type": "text", "text": f"Error: {response['error']}"}],
                    is_error=True
                )

            # Convert result to MCP content format
            result = response.get("result", {})
            content = []

            if isinstance(result, dict):
                content.append({
                    "type": "text",
                    "text": json.dumps(result, indent=2)
                })
            else:
                content.append({
                    "type": "text",
                    "text": str(result)
                })

            return MCPToolResult(content=content, is_error=False)

        except Exception as e:
            logger.error(f"Error calling MCP tool: {e}")
            return MCPToolResult(
                content=[{"type": "text", "text": f"Error: {str(e)}"}],
                is_error=True
            )

    async def list_tools(self) -> List[Dict[str, Any]]:
        """List available MCP tools"""
        if not self.process:
            return []

        request = {
            "jsonrpc": "2.0",
            "id": "list_tools",
            "method": "tools/list",
            "params": {}
        }

        try:
            request_json = json.dumps(request).encode() + b'\n'
            self.process.stdin.write(request_json)
            await self.process.stdin.drain()

            response_line = await self.process.stdout.readline()
            response = json.loads(response_line.decode().strip())

            if "error" in response:
                logger.error(f"MCP list tools error: {response['error']}")
                return []

            return response.get("result", {}).get("tools", [])

        except Exception as e:
            logger.error(f"Error listing MCP tools: {e}")
            return []

class UnifiedOrchestratorClient:
    """Unified client supporting both HTTP API and MCP transports"""

    def __init__(self, transport: str = "auto", **kwargs):
        """
        Initialize unified client

        Args:
            transport: "http", "mcp", or "auto" (tries MCP first, falls back to HTTP)
            **kwargs: Transport-specific arguments
                For HTTP: base_url
                For MCP: server_command
        """
        self.transport = transport
        self.http_client = None
        self.mcp_client = None

        if transport in ["http", "auto"]:
            base_url = kwargs.get("base_url", "http://localhost:8765")
            self.http_client = AIOrchestratorClient(base_url=base_url)

        if transport in ["mcp", "auto"]:
            server_command = kwargs.get("server_command", ["python", "-m", "orchestrator.mcp_server"])
            self.mcp_client = MCPClient(server_command)

        self.active_transport = None
        self.connected = False

    async def connect(self) -> bool:
        """Connect to orchestrator service"""
        if self.transport == "http":
            # HTTP only
            self.active_transport = "http"
            self.connected = True  # HTTP is connectionless
            return True

        elif self.transport == "mcp":
            # MCP only
            if await self.mcp_client.start_server():
                self.active_transport = "mcp"
                self.connected = True
                return True
            return False

        elif self.transport == "auto":
            # Try MCP first, fallback to HTTP
            if self.mcp_client and await self.mcp_client.start_server():
                self.active_transport = "mcp"
                self.connected = True
                logger.info("Connected using MCP transport")
                return True
            elif self.http_client:
                self.active_transport = "http"
                self.connected = True
                logger.info("Connected using HTTP transport (MCP fallback)")
                return True
            else:
                logger.error("No transport available")
                return False

        return False

    async def disconnect(self):
        """Disconnect from orchestrator service"""
        if self.mcp_client:
            await self.mcp_client.stop_server()

        self.connected = False
        self.active_transport = None

    async def orchestrate_task(self, task: str, context: str = None, **kwargs) -> Dict[str, Any]:
        """Orchestrate task using available transport"""
        if not self.connected:
            raise ConnectionError("Not connected to orchestrator")

        if self.active_transport == "mcp" and self.mcp_client:
            return await self._orchestrate_task_mcp(task, context, **kwargs)
        elif self.active_transport == "http" and self.http_client:
            return await self._orchestrate_task_http(task, context, **kwargs)
        else:
            raise RuntimeError("No active transport available")

    async def _orchestrate_task_mcp(self, task: str, context: str = None, **kwargs) -> Dict[str, Any]:
        """Orchestrate task using MCP"""
        arguments = {
            "task": task,
            "context": context or "",
            "project_type": kwargs.get("project_type", "web_app"),
            "use_rag": kwargs.get("use_rag", True)
        }

        result = await self.mcp_client.call_tool("orchestrate_task", arguments)

        if result.is_error:
            raise RuntimeError(f"MCP orchestration failed: {result.content}")

        # Parse MCP response
        response_text = result.content[0]["text"] if result.content else "{}"
        return json.loads(response_text)

    async def _orchestrate_task_http(self, task: str, context: str = None, **kwargs) -> Dict[str, Any]:
        """Orchestrate task using HTTP (legacy)"""
        return await self.http_client.orchestrate_task(task, context, **kwargs)

    async def query_knowledge(self, query: str, context: str = None, **kwargs) -> Dict[str, Any]:
        """Query knowledge base"""
        if not self.connected:
            raise ConnectionError("Not connected to orchestrator")

        if self.active_transport == "mcp" and self.mcp_client:
            return await self._query_knowledge_mcp(query, context, **kwargs)
        elif self.active_transport == "http" and self.http_client:
            # HTTP fallback - limited functionality
            return await self._query_knowledge_http(query, context, **kwargs)
        else:
            raise RuntimeError("No active transport available")

    async def _query_knowledge_mcp(self, query: str, context: str = None, **kwargs) -> Dict[str, Any]:
        """Query knowledge using MCP"""
        arguments = {
            "query": query,
            "context": context or "",
            "max_results": kwargs.get("max_results", 5)
        }

        result = await self.mcp_client.call_tool("query_knowledge", arguments)

        if result.is_error:
            raise RuntimeError(f"MCP knowledge query failed: {result.content}")

        response_text = result.content[0]["text"] if result.content else "{}"
        return json.loads(response_text)

    async def _query_knowledge_http(self, query: str, context: str = None, **kwargs) -> Dict[str, Any]:
        """Query knowledge using HTTP (limited)"""
        # This would need to be implemented in the HTTP API
        # For now, return a placeholder
        return {
            "answer": f"Knowledge query for: {query} (HTTP fallback - limited functionality)",
            "sources": [],
            "confidence": 0.0
        }

# Legacy HTTP-only client for backward compatibility
class AIOrchestratorClient:
    """Legacy HTTP-only client for backward compatibility"""

    def __init__(self, base_url: str = "http://localhost:8765"):
        self.base_url = base_url.rstrip('/')
        self.session = None
        self._initialize_session()

    def _initialize_session(self):
        """Initialize HTTP session"""
        if AIOHTTP_AVAILABLE:
            # Async version
            pass  # Will create session when needed
        else:
            # Sync fallback
            pass

    async def _ensure_session(self):
        """Ensure active aiohttp session"""
        if AIOHTTP_AVAILABLE and self.session is None:
            timeout = aiohttp.ClientTimeout(total=30)
            self.session = aiohttp.ClientSession(timeout=timeout)

    async def close(self):
        """Close session"""
        if self.session:
            await self.session.close()
            self.session = None

    async def _post_request(self, endpoint: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Send POST request to orchestrator"""
        await self._ensure_session()
        url = f"{self.base_url}{endpoint}"

        try:
            if self.session:  # Async version
                async with self.session.post(url, json=data) as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        error_text = await response.text()
                        raise Exception(f"HTTP {response.status}: {error_text}")
            else:  # Sync fallback
                if not AIOHTTP_AVAILABLE:
                    import requests
                    response = requests.post(url, json=data, timeout=30)
                    response.raise_for_status()
                    return response.json()
                else:
                    raise Exception("No HTTP session available")

        except Exception as e:
            logger.error(f"Request to {endpoint} failed: {e}")
            raise

    async def health_check(self) -> Dict[str, Any]:
        """Service health check"""
        try:
            await self._ensure_session()
            if self.session:
                async with self.session.get(f"{self.base_url}/") as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        return {"status": "unhealthy", "error": f"HTTP {response.status}"}
            else:
                import requests
                response = requests.get(f"{self.base_url}/", timeout=5)
                response.raise_for_status()
                return response.json()
        except Exception as e:
            return {"status": "error", "error": str(e)}

    async def analyze_project(self, project_path: str = ".") -> Dict[str, Any]:
        """Project analysis"""
        data = {"project_path": project_path}
        return await self._post_request("/api/analyze-project", data)

    async def select_rules(self, task: str, project_context: Dict[str, Any] = None,
                          current_rules: List[str] = None) -> Dict[str, Any]:
        """Select appropriate rules for a task"""
        data = {
            "task": task,
            "project_context": project_context or {},
            "current_rules": current_rules or []
        }
        return await self._post_request("/api/select-rules", data)

    async def generate_plan(self, task: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Generate execution plan"""
        data = {
            "task": task,
            "context": context or {}
        }
        return await self._post_request("/api/generate-plan", data)

    async def get_recommendations(self, code: str = "", task: str = "") -> Dict[str, Any]:
        """Get recommendations"""
        data = {
            "code": code,
            "task": task
        }
        return await self._post_request("/api/get-recommendations", data)

    async def orchestrate_task(self, task: str, project_path: str = ".") -> Dict[str, Any]:
        """Full task orchestration"""
        data = {
            "task": task,
            "project_path": project_path
        }
        return await self._post_request("/api/orchestrate-task", data)

    async def analyze_code(self, code: str, language: str = "python", task: str = "") -> Dict[str, Any]:
        """Analyze source code"""
        data = {
            "code": code,
            "language": language,
            "task": task
        }
        return await self._post_request("/api/analyze-code", data)

    async def get_context(self, project_path: str = ".") -> Dict[str, Any]:
        """Get project context"""
        data = {"project_path": project_path}
        return await self._post_request("/api/get-context", data)

    # Convenience methods for Cursor Agent Rules

    async def get_optimal_rules_for_task(self, task_description: str,
                                       current_file: str = "",
                                       project_type: str = "") -> List[str]:
        """Get optimal rules for a task (primary method for agent)"""
        try:
            # Pobierz kontekst projektu
            context = await self.get_context()
            project_context = context.get('project_context', {}) if context.get('success') else {}

            # Dodaj informacje o aktualnym pliku
            if current_file:
                project_context['current_file'] = current_file

            # Wybierz rules
            rules_result = await self.select_rules(
                task=task_description,
                project_context=project_context,
                current_rules=[]
            )

            if rules_result.get('success'):
                selection = rules_result['rules_selection']
                return selection.get('recommended_rules', [])
            else:
                logger.warning(f"Failed to get rules: {rules_result.get('error')}")
                return ['30_hybrid_moe_tot_reasoning', '31_advanced_agent_steering']

        except Exception as e:
            logger.error(f"Error getting optimal rules: {e}")
            return ['30_hybrid_moe_tot_reasoning', '31_advanced_agent_steering']

    async def get_task_plan(self, task_description: str) -> Dict[str, Any]:
        """Get execution plan for a task"""
        try:
            context = await self.get_context()
            project_context = context.get('project_context', {}) if context.get('success') else {}

            plan_result = await self.generate_plan(
                task=task_description,
                context=project_context
            )

            if plan_result.get('success'):
                return plan_result['execution_plan']
            else:
                return {"plan": {}, "reasoning": "Failed to generate plan"}

        except Exception as e:
            logger.error(f"Error getting task plan: {e}")
            return {"plan": {}, "reasoning": f"Error: {e}"}

    async def get_code_insights(self, code: str, task_context: str = "") -> List[str]:
        """Get insights for code"""
        try:
            analysis_result = await self.analyze_code(
                code=code,
                task=task_context
            )

            if analysis_result.get('success'):
                return analysis_result.get('recommendations', [])
            else:
                return []

        except Exception as e:
            logger.error(f"Error getting code insights: {e}")
            return []

    async def get_project_insights(self) -> Dict[str, Any]:
        """Get insights for the entire project"""
        try:
            analysis = await self.analyze_project()
            if analysis.get('success'):
                return analysis['project_analysis']
            else:
                return {}

        except Exception as e:
            logger.error(f"Error getting project insights: {e}")
            return {}

    # Synchronous versions for easier integration

    def get_optimal_rules_sync(self, task_description: str,
                             current_file: str = "",
                             project_type: str = "") -> List[str]:
        """Synchronous version of get_optimal_rules_for_task"""
        try:
            # Run async function in new event loop
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            result = loop.run_until_complete(
                self.get_optimal_rules_for_task(task_description, current_file, project_type)
            )
            loop.close()
            return result
        except Exception as e:
            logger.error(f"Sync rules selection failed: {e}")
            return ['30_hybrid_moe_tot_reasoning', '31_advanced_agent_steering']

    def get_task_plan_sync(self, task_description: str) -> Dict[str, Any]:
        """Synchronous version of get_task_plan"""
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            result = loop.run_until_complete(self.get_task_plan(task_description))
            loop.close()
            return result
        except Exception as e:
            logger.error(f"Sync plan generation failed: {e}")
            return {"plan": {}, "reasoning": f"Error: {e}"}

    def get_code_insights_sync(self, code: str, task_context: str = "") -> List[str]:
        """Synchronous version of get_code_insights"""
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            result = loop.run_until_complete(self.get_code_insights(code, task_context))
            loop.close()
            return result
        except Exception as e:
            logger.error(f"Sync code insights failed: {e}")
            return []


# Global instance for easy access
_orchestrator_client = None

def get_orchestrator_client(base_url: str = "http://localhost:8765") -> AIOrchestratorClient:
    """Get global orchestrator client instance"""
    global _orchestrator_client
    if _orchestrator_client is None:
        _orchestrator_client = AIOrchestratorClient(base_url)
    return _orchestrator_client


# Convenience functions for Cursor Agent Rules

def select_optimal_rules(task: str, current_file: str = "", project_type: str = "") -> List[str]:
    """Convenience function to get optimal rules for a task"""
    client = get_orchestrator_client()
    return client.get_optimal_rules_sync(task, current_file, project_type)

def get_execution_plan(task: str) -> Dict[str, Any]:
    """Convenience function to get execution plan"""
    client = get_orchestrator_client()
    return client.get_task_plan_sync(task)

def analyze_code_for_insights(code: str, context: str = "") -> List[str]:
    """Convenience function to analyze code"""
    client = get_orchestrator_client()
    return client.get_code_insights_sync(code, context)

def get_project_context() -> Dict[str, Any]:
    """Convenience function to get project context"""
    try:
        client = get_orchestrator_client()
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(client.get_project_insights())
        loop.close()
        return result
    except Exception as e:
        logger.error(f"Failed to get project context: {e}")
        return {}


# Example usage in Cursor Agent Rules:

"""
Example: How to use in .cursor/rules/31_advanced_agent_steering.mdc

```python
# In agent rule implementation:

from ai_orchestrator_client import select_optimal_rules, get_execution_plan

def enhance_agent_capabilities(task_description, current_context):
    # Get optimal rules for this task
    optimal_rules = select_optimal_rules(
        task=task_description,
        current_file=current_context.get('file', ''),
        project_type=current_context.get('project_type', '')
    )

    # Get execution plan
    plan = get_execution_plan(task_description)

    # Apply selected rules in optimal order
    for rule_name in optimal_rules:
        apply_rule(rule_name, task_description, plan)

    return enhanced_result
```

This allows Cursor Agent to dynamically adapt its behavior based on:
- Task complexity and requirements
- Project context and tech stack
- Available rules and their priorities
- AI-powered insights and recommendations
"""
