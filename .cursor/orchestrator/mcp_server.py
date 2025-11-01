#!/usr/bin/env python3
"""
MCP (Model Context Protocol) Server for AI Orchestrator
MCP server implementation using stdio for communication
"""

import asyncio
import json
import logging
import sys
from typing import Dict, Any, List, Optional, Union
from dataclasses import dataclass
from datetime import datetime

try:
    # When run as module
    from .ai_orchestrator import AIOrchestrator
    from .rag_engine import RAGEngine
    from .ai_simple_config import AISimpleConfig
except ImportError:
    # When run directly as script
    import sys
    from pathlib import Path
    current_dir = Path(__file__).parent
    if str(current_dir) not in sys.path:
        sys.path.insert(0, str(current_dir))
    from ai_orchestrator import AIOrchestrator
    from rag_engine import RAGEngine
    from ai_simple_config import AISimpleConfig

# Configure logging to stderr only - stdout must be reserved for JSON-RPC
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stderr  # All logs to stderr, stdout only for JSON-RPC
)

logger = logging.getLogger(__name__)

@dataclass
class MCPTool:
    """MCP Tool definition"""
    name: str
    description: str
    input_schema: Dict[str, Any]

@dataclass
class MCPResource:
    """MCP Resource definition"""
    uri: str
    name: str
    description: str
    mime_type: str = "application/json"

@dataclass
class MCPRequest:
    """MCP Request - JSON-RPC 2.0 compatible"""
    id: Optional[Union[str, int]]  # Can be string, number, or null/None
    method: str
    params: Dict[str, Any]

@dataclass
class MCPResponse:
    """MCP Response - JSON-RPC 2.0 compatible"""
    id: Optional[Union[str, int]]  # Can be string, number, or null/None
    result: Optional[Dict[str, Any]] = None
    error: Optional[Dict[str, Any]] = None

class OrchestratorMCPServer:
    """MCP Server for AI Orchestrator with RAG"""

    def __init__(self):
        self.config = AISimpleConfig(".")
        self.orchestrator = AIOrchestrator()
        self.rag_engine = RAGEngine(self.config)
        self.tools = self._initialize_tools()
        self.resources = self._initialize_resources()

    def _initialize_tools(self) -> List[MCPTool]:
        """Initialize available MCP tools"""
        return [
            MCPTool(
                name="orchestrate_task",
                description="Complete task orchestration with intelligent rule selection and planning",
                input_schema={
                    "type": "object",
                    "properties": {
                        "task": {
                            "type": "string",
                            "description": "Task description to execute"
                        },
                        "context": {
                            "type": "string",
                            "description": "Additional project context"
                        },
                        "project_type": {
                            "type": "string",
                            "enum": ["web_app", "api_microservices", "ml_ai", "mobile_app", "iot_embedded"],
                            "description": "Project type"
                        },
                        "use_rag": {
                            "type": "boolean",
                            "default": True,
                            "description": "Whether to use RAG to enrich context"
                        }
                    },
                    "required": ["task"]
                }
            ),
            MCPTool(
                name="select_rules",
                description="Selection of optimal rules for the given context",
                input_schema={
                    "type": "object",
                    "properties": {
                        "task_description": {
                            "type": "string",
                            "description": "Task description"
                        },
                        "current_file": {
                            "type": "string",
                            "description": "Currently edited file"
                        },
                        "project_type": {
                            "type": "string",
                            "description": "Project type"
                        }
                    },
                    "required": ["task_description"]
                }
            ),
            MCPTool(
                name="get_execution_plan",
                description="Generation of detailed task execution plan",
                input_schema={
                    "type": "object",
                    "properties": {
                        "task": {
                            "type": "string",
                            "description": "Task description"
                        },
                        "context": {
                            "type": "string",
                            "description": "Project context"
                        }
                    },
                    "required": ["task"]
                }
            ),
            MCPTool(
                name="query_knowledge",
                description="Knowledge base search using RAG",
                input_schema={
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "Query to knowledge base"
                        },
                        "context": {
                            "type": "string",
                            "description": "Additional context for search"
                        },
                        "max_results": {
                            "type": "integer",
                            "default": 5,
                            "minimum": 1,
                            "maximum": 10,
                            "description": "Maximum number of results"
                        }
                    },
                    "required": ["query"]
                }
            ),
            MCPTool(
                name="analyze_code",
                description="Code analysis with project context",
                input_schema={
                    "type": "object",
                    "properties": {
                        "code": {
                            "type": "string",
                            "description": "Code to analyze"
                        },
                        "context": {
                            "type": "string",
                            "description": "Project context"
                        },
                        "language": {
                            "type": "string",
                            "description": "Programming language"
                        }
                    },
                    "required": ["code"]
                }
            )
        ]

    def _initialize_resources(self) -> List[MCPResource]:
        """Initialize available MCP resources"""
        return [
            MCPResource(
                uri="orchestrator://knowledge",
                name="Knowledge Base",
                description="Index of the entire AI Orchestrator knowledge base",
                mime_type="application/json"
            ),
            MCPResource(
                uri="orchestrator://rules",
                name="System Rules",
                description="List of available rules and their configurations",
                mime_type="application/json"
            ),
            MCPResource(
                uri="orchestrator://metrics",
                name="Performance Metrics",
                description="System performance statistics",
                mime_type="application/json"
            ),
            MCPResource(
                uri="orchestrator://config",
                name="Configuration",
                description="Current system configuration",
                mime_type="application/json"
            )
        ]

    async def handle_request(self, request: MCPRequest) -> MCPResponse:
        """Handle MCP request"""
        try:
            if request.method == "initialize":
                return await self._handle_initialize(request)
            elif request.method == "tools/list":
                return await self._handle_tools_list(request)
            elif request.method == "tools/call":
                return await self._handle_tools_call(request)
            elif request.method == "resources/list":
                return await self._handle_resources_list(request)
            elif request.method == "resources/read":
                return await self._handle_resources_read(request)
            elif request.method == "prompts/list":
                return await self._handle_prompts_list(request)
            elif request.method == "ping":
                return await self._handle_ping(request)
            else:
                # Method not found - return error response
                return self._create_error_response(
                    request.id, -32601, f"Method not found: {request.method}"
                )
        except Exception as e:
            logger.error(f"Error handling request {request.id}: {e}")
            return self._create_error_response(
                request.id, -32603, f"Internal error: {str(e)}"
            )

    def _create_error_response(self, request_id: Optional[Union[str, int]],
                              error_code: int, error_message: str) -> MCPResponse:
        """Create proper error response (no result field)"""
        return MCPResponse(
            id=request_id,
            error={
                "code": error_code,
                "message": error_message
            }
        )

    async def _handle_initialize(self, request: MCPRequest) -> MCPResponse:
        """Handle initialization with full MCP capabilities"""
        return MCPResponse(
            id=request.id,
            result={
                "protocolVersion": "2024-11-05",
                "capabilities": {
                    "tools": {
                        "listChanged": True
                    },
                    "resources": {
                        "listChanged": True,
                        "subscribe": True
                    },
                    "prompts": {
                        "listChanged": True
                    },
                    "logging": {}
                },
                "serverInfo": {
                    "name": "ai-orchestrator",
                    "version": "2.0.0",
                    "description": "AI-powered task orchestrator with RAG knowledge retrieval",
                    "license": "MIT"
                }
            }
        )

    async def _handle_tools_list(self, request: MCPRequest) -> MCPResponse:
        """Handle tools list request"""
        tools_list = []
        for tool in self.tools:
            tools_list.append({
                "name": tool.name,
                "description": tool.description,
                "inputSchema": tool.input_schema
            })

        return MCPResponse(
            id=request.id,
            result={"tools": tools_list}
        )

    async def _handle_tools_call(self, request: MCPRequest) -> MCPResponse:
        """Handle tool call request"""
        tool_name = request.params.get("name")
        tool_args = request.params.get("arguments", {})

        # Find tool
        tool = next((t for t in self.tools if t.name == tool_name), None)
        if not tool:
            return MCPResponse(
                id=request.id,
                error={
                    "code": -32602,
                    "message": f"Tool not found: {tool_name}"
                }
            )

        # Execute tool
        try:
            result = await self._execute_tool(tool_name, tool_args)
            return MCPResponse(
                id=request.id,
                result=result
            )
        except Exception as e:
            logger.error(f"Error executing tool {tool_name}: {e}")
            return MCPResponse(
                id=request.id,
                error={
                    "code": -32603,
                    "message": f"Tool execution error: {str(e)}"
                }
            )

    async def _execute_tool(self, tool_name: str, args: Dict[str, Any]) -> Dict[str, Any]:
        """Execute specific tool"""

        if tool_name == "orchestrate_task":
            return await self._orchestrate_task(args)

        elif tool_name == "select_rules":
            return await self._select_rules(args)

        elif tool_name == "get_execution_plan":
            return await self._get_execution_plan(args)

        elif tool_name == "query_knowledge":
            return await self._query_knowledge(args)

        elif tool_name == "analyze_code":
            return await self._analyze_code(args)

        else:
            raise ValueError(f"Unknown tool: {tool_name}")

    async def _orchestrate_task(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Execute orchestrate_task tool"""
        task = args["task"]
        context = args.get("context", "")
        project_type = args.get("project_type", "web_app")
        use_rag = args.get("use_rag", True)

        # Use RAG to enhance context if requested
        enhanced_context = context
        rag_sources = []

        if use_rag and context:
            rag_result = await self.rag_engine.query_knowledge(
                query=f"Best practices for: {task}",
                context=context
            )
            enhanced_context = context + "\n\nRAG Context:\n" + rag_result.answer
            rag_sources = [s.metadata for s in rag_result.sources]

        # Execute orchestration
        result = await self.orchestrator.orchestrate_project(
            task_description=task,
            context=enhanced_context,
            project_type=project_type
        )

        return {
            "plan": result.execution_plan,
            "rules": result.selected_rules,
            "confidence": result.confidence,
            "rag_sources": rag_sources,
            "enhanced_context_used": use_rag
        }

    async def _select_rules(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Execute select_rules tool"""
        task_description = args["task_description"]
        current_file = args.get("current_file", "")
        project_type = args.get("project_type", "web_app")

        # Use orchestrator to select rules
        rules = await self.orchestrator.select_optimal_rules(
            task_description=task_description,
            current_file=current_file,
            project_type=project_type
        )

        return {
            "selected_rules": rules,
            "rationale": "Rules selected based on task analysis and project context"
        }

    async def _get_execution_plan(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Execute get_execution_plan tool"""
        task = args["task"]
        context = args.get("context", "")

        # Generate execution plan
        plan = await self.orchestrator.generate_execution_plan(
            task_description=task,
            context=context
        )

        return {
            "execution_plan": plan,
            "estimated_duration": "Based on task complexity",
            "risk_assessment": "Low to medium"
        }

    async def _query_knowledge(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Execute query_knowledge tool"""
        query = args["query"]
        context = args.get("context", "")
        max_results = args.get("max_results", 5)

        # Query RAG engine
        result = await self.rag_engine.query_knowledge(
            query=query,
            context=context,
            max_results=max_results
        )

        return {
            "answer": result.answer,
            "sources": [s.metadata for s in result.sources],
            "confidence": result.confidence_score,
            "reasoning": result.reasoning_trace
        }

    async def _analyze_code(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Execute analyze_code tool"""
        code = args["code"]
        context = args.get("context", "")
        language = args.get("language", "python")

        # Use orchestrator for code analysis
        analysis = await self.orchestrator.analyze_code(
            code=code,
            context=context,
            language=language
        )

        return {
            "analysis": analysis,
            "recommendations": "Based on best practices and project context",
            "issues_found": len(analysis.get("issues", []))
        }

    async def _handle_resources_list(self, request: MCPRequest) -> MCPResponse:
        """Handle resources list request"""
        resources_list = []
        for resource in self.resources:
            resources_list.append({
                "uri": resource.uri,
                "name": resource.name,
                "description": resource.description,
                "mimeType": resource.mime_type
            })

        return MCPResponse(
            id=request.id,
            result={"resources": resources_list}
        )

    async def _handle_resources_read(self, request: MCPRequest) -> MCPResponse:
        """Handle resource read request"""
        uri = request.params.get("uri")

        # Find resource
        resource = next((r for r in self.resources if r.uri == uri), None)
        if not resource:
            return MCPResponse(
                id=request.id,
                error={
                    "code": -32602,
                    "message": f"Resource not found: {uri}"
                }
            )

        # Read resource content
        try:
            content = await self._read_resource(uri)
            return MCPResponse(
                id=request.id,
                result={
                    "contents": [{
                        "uri": uri,
                        "mimeType": resource.mime_type,
                        "text": content
                    }]
                }
            )
        except Exception as e:
            return MCPResponse(
                id=request.id,
                error={
                    "code": -32603,
                    "message": f"Resource read error: {str(e)}"
                }
            )

    async def _read_resource(self, uri: str) -> str:
        """Read resource content"""

        if uri == "orchestrator://knowledge":
            # Return knowledge base index
            try:
                index = await self.rag_engine.get_knowledge_index()
                return json.dumps(index, indent=2)
            except Exception:
                return json.dumps({"status": "not_initialized", "message": "RAG engine not ready"})

        elif uri == "orchestrator://rules":
            # Return rules information
            rules_info = {
                "available_rules": ["security_basics", "performance_optimization", "code_quality", "docker_basics"],
                "categories": ["security", "performance", "quality", "orchestration"],
                "total_rules": 13
            }
            return json.dumps(rules_info, indent=2)

        elif uri == "orchestrator://metrics":
            # Return performance metrics
            metrics = {
                "uptime": "TBD",
                "queries_processed": 0,
                "rag_enabled": True,
                "mcp_capable": True
            }
            return json.dumps(metrics, indent=2)

        elif uri == "orchestrator://config":
            # Return configuration info
            config_info = {
                "version": "2.0.0",
                "features": ["RAG", "MCP", "AI_Orchestration"],
                "knowledge_base_size": "TBD",
                "supported_models": ["claude_3_5_sonnet", "gpt_4o", "gpt_4o_mini"]
            }
            return json.dumps(config_info, indent=2)

        else:
            raise ValueError(f"Unknown resource: {uri}")

    async def _handle_prompts_list(self, request: MCPRequest) -> MCPResponse:
        """Handle prompts list request"""
        prompts_list = [
            {
                "name": "orchestrate_task",
                "description": "Create a comprehensive task orchestration plan",
                "arguments": [
                    {
                        "name": "task",
                        "description": "The task to orchestrate",
                        "required": True
                    },
                    {
                        "name": "context",
                        "description": "Additional project context",
                        "required": False
                    }
                ]
            },
            {
                "name": "analyze_code",
                "description": "Analyze code for best practices and improvements",
                "arguments": [
                    {
                        "name": "code",
                        "description": "The code to analyze",
                        "required": True
                    }
                ]
            }
        ]

        return MCPResponse(
            id=request.id,
            result={"prompts": prompts_list}
        )

    async def _handle_ping(self, request: MCPRequest) -> MCPResponse:
        """Handle ping request for health check"""
        return MCPResponse(
            id=request.id,
            result={"status": "ok", "timestamp": "2025-10-31T22:15:00Z"}
        )

class MCPStdIOServer:
    """MCP Server używający stdio do komunikacji"""

    def __init__(self):
        self.server = OrchestratorMCPServer()

    async def run(self):
        """Run MCP server with stdio communication"""
        logger.info("Starting MCP Server with stdio transport")

        # Initialize RAG engine
        await self.server.rag_engine.initialize_knowledge_base()

        # Start knowledge monitoring in background
        monitor_task = asyncio.create_task(
            self.server.rag_engine.start_knowledge_monitoring(interval=30)
        )

        try:
            while True:
                # Read line from stdin
                line = await asyncio.get_event_loop().run_in_executor(
                    None, sys.stdin.readline
                )

                if not line:
                    break

                try:
                    # Parse JSON request
                    request_data = json.loads(line.strip())
                    request = MCPRequest(
                        id=request_data.get("id"),
                        method=request_data.get("method"),
                        params=request_data.get("params", {})
                    )

                    # Handle request - skip notifications (no id = no response needed)
                    if request.id is None:
                        logger.debug(f"Received notification: {request.method}")
                        continue

                    response = await self.server.handle_request(request)

                    # Send response to stdout
                    response_data = {
                        "jsonrpc": "2.0",
                        "id": response.id
                    }

                    # Add either result OR error, never both
                    if response.error is not None:
                        response_data["error"] = response.error
                    elif response.result is not None:
                        response_data["result"] = response.result
                    else:
                        # Invalid response - neither result nor error
                        response_data["error"] = {
                            "code": -32603,
                            "message": "Internal error: Invalid response format"
                        }

                    # Debug logging of response being sent
                    logger.debug(f"Sending MCP response: {json.dumps(response_data)}")

                    # Send response with flush
                    print(json.dumps(response_data), flush=True)
                    sys.stdout.flush()

                except json.JSONDecodeError as e:
                    logger.error(f"Invalid JSON received: {e}")
                    # Send error response (no id for parse errors)
                    error_response = {
                        "jsonrpc": "2.0",
                        "error": {
                            "code": -32700,
                            "message": "Parse error"
                        }
                    }
                    print(json.dumps(error_response), flush=True)

                except Exception as e:
                    logger.error(f"Error processing request: {e}")
                    # Send error response (no id for internal errors)
                    error_response = {
                        "jsonrpc": "2.0",
                        "error": {
                            "code": -32603,
                            "message": "Internal error"
                        }
                    }
                    print(json.dumps(error_response), flush=True)

        except KeyboardInterrupt:
            logger.info("MCP Server shutting down")
            # Stop knowledge monitoring
            try:
                self.server.rag_engine.stop_knowledge_monitoring()
            except Exception as e:
                logger.error(f"Error stopping knowledge monitoring: {e}")
        except Exception as e:
            logger.error(f"MCP Server error: {e}")
            # Stop knowledge monitoring on error
            try:
                self.server.rag_engine.stop_knowledge_monitoring()
            except Exception as cleanup_error:
                logger.error(f"Error stopping knowledge monitoring: {cleanup_error}")

# Convenience function to start MCP server
async def start_mcp_server():
    """Start the MCP server"""
    server = MCPStdIOServer()
    await server.run()

if __name__ == "__main__":
    # Start MCP server
    asyncio.run(start_mcp_server())
