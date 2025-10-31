#!/usr/bin/env python3
"""
AI-Powered Universal Cursor Orchestrator - Minimal MCP Version
Only essential methods for MCP server compatibility
"""

import asyncio
import json
import logging
import os
import sys
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Any, Union

# Import simple config system
try:
    from .ai_simple_config import AISimpleConfig
except ImportError:
    import sys
    from pathlib import Path
    current_dir = Path(__file__).parent
    if str(current_dir) not in sys.path:
        sys.path.insert(0, str(current_dir))
    from ai_simple_config import AISimpleConfig

# Logging configuration - stderr only for MCP compatibility
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stderr  # stderr only, stdout reserved for JSON-RPC
)
logger = logging.getLogger(__name__)

class ProjectType(Enum):
    WEB_APP = "web_app"
    API_MICROSERVICES = "api_microservices"
    ML_AI = "ml_ai"
    MOBILE_APP = "mobile_app"
    IOT_EMBEDDED = "iot_embedded"

@dataclass
class ProjectContext:
    tech_stack: List[str] = field(default_factory=list)
    architecture: str = "unknown"
    domain: str = "unknown"
    scale: str = "small"
    files_analyzed: int = 0
    loc_estimated: int = 0

@dataclass
class AgentAllocation:
    planner: float = 0.2
    reasoner: float = 0.3
    implementer: float = 0.3
    tester: float = 0.1
    refactorer: float = 0.1
    security_expert: bool = False
    architecture_expert: bool = False
    devops_expert: bool = False
    performance_expert: bool = False

@dataclass
class OrchestrationResult:
    project_type: ProjectType = ProjectType.WEB_APP
    agent_allocation: AgentAllocation = field(default_factory=AgentAllocation)
    recommendations: List[str] = field(default_factory=list)
    next_actions: List[str] = field(default_factory=list)
    ai_reasoning: str = ""
    metrics: Dict[str, Any] = field(default_factory=dict)

class AIOrchestrator:
    """Minimal AI Orchestrator for MCP compatibility"""

    def __init__(self):
        self.config = AISimpleConfig(str(Path(__file__).parent))
        self.ai_client = None  # Will be None for MCP compatibility

        # Initialize with basic config
        try:
            self.config.load_config()
            logger.info("🤖 AI-Powered Cursor Orchestrator initialized with simple config")
        except Exception as e:
            logger.warning(f"⚠️ AI features unavailable: {e}")
            logger.info("💡 Basic analysis will work, AI features disabled")

    async def orchestrate_project(self, project_path: str) -> OrchestrationResult:
        """Full AI project orchestration - minimal implementation"""
        logger.info(f"🚀 Starting AI-powered project orchestration for: {project_path}")

        # Basic project analysis
        context = await self._analyze_project_basic(project_path)

        # Determine project type
        project_type = self._classify_project_type(context)

        # Basic agent allocation
        allocation = AgentAllocation()

        # Generate basic recommendations
        recommendations = [
            "Implement proper error handling",
            "Add comprehensive logging",
            "Create unit tests",
            "Set up CI/CD pipeline"
        ]

        next_actions = [
            "Review project structure",
            "Identify key components",
            "Plan implementation phases",
            "Setup development environment"
        ]

        result = OrchestrationResult(
            project_type=project_type,
            agent_allocation=allocation,
            recommendations=recommendations,
            next_actions=next_actions,
            ai_reasoning="Basic project analysis completed. AI features not available in minimal mode.",
            metrics={
                "quality_score": 0.7,
                "success_rate": 0.8,
                "files_analyzed": context.files_analyzed,
                "tech_stack": context.tech_stack
            }
        )

        logger.info(f"📋 AI-Powered Orchestration Result: {project_type.value}, Quality: {result.metrics['quality_score']:.2f}")
        return result

    async def select_optimal_rules(self, task_description: str, current_file: str = None,
                                 project_type: str = None) -> List[str]:
        """Select optimal rules for the task - minimal implementation"""
        logger.info(f"🎯 Selecting optimal rules for: {task_description[:50]}...")

        # Basic rule selection based on task type
        base_rules = ["99_orchestrator_automation"]

        if "security" in task_description.lower():
            base_rules.extend(["20_security_basics"])
        if "docker" in task_description.lower() or "container" in task_description.lower():
            base_rules.extend(["40_docker_basics"])
        if "test" in task_description.lower():
            base_rules.extend(["35_code_quality_assurance"])

        # Add reasoning and steering rules
        base_rules.extend(["30_hybrid_moe_tot_reasoning", "31_advanced_agent_steering"])

        logger.info(f"📋 Selected {len(base_rules)} rules: {', '.join(base_rules[:3])}...")
        return base_rules

    async def generate_execution_plan(self, task: str, context: str = None) -> Dict[str, Any]:
        """Generate execution plan - minimal implementation"""
        logger.info(f"📋 Generating AI execution plan for: {task[:50]}...")

        plan = {
            "Planning": {
                "tasks": ["Analyze requirements", "Design solution", "Identify risks"],
                "estimated_time": "2-4 hours",
                "agents": ["Planner", "Reasoner"]
            },
            "Implementation": {
                "tasks": ["Write code", "Add tests", "Documentation"],
                "estimated_time": "4-8 hours",
                "agents": ["Implementer", "Tester"]
            },
            "Review": {
                "tasks": ["Code review", "Testing", "Deployment preparation"],
                "estimated_time": "2-4 hours",
                "agents": ["Reviewer", "DevOps"]
            }
        }

        logger.info("🤖 AI-Generated Execution Plan completed")
        return plan

    async def analyze_code(self, code: str, context: str = None, language: str = None) -> Dict[str, Any]:
        """Analyze code - minimal implementation"""
        logger.info(f"🔍 Analyzing code ({len(code)} chars) in {language or 'unknown'}...")

        analysis = {
            "language": language or "unknown",
            "lines_of_code": len(code.split('\n')),
            "complexity": "medium",
            "issues": [
                "Consider adding error handling",
                "Add docstrings for functions",
                "Consider breaking into smaller functions"
            ],
            "suggestions": [
                "Use type hints",
                "Add unit tests",
                "Follow PEP 8 style guide"
            ],
            "quality_score": 0.75
        }

        logger.info(f"✅ Code analysis completed - Quality: {analysis['quality_score']:.2f}")
        return analysis

    async def _analyze_project_basic(self, project_path: str) -> ProjectContext:
        """Basic project analysis without AI"""
        context = ProjectContext()
        project_dir = Path(project_path)

        if not project_dir.exists():
            logger.warning(f"Project path does not exist: {project_path}")
            return context

        # Basic file analysis
        file_count = 0
        loc_count = 0
        tech_stack = set()

        for file_path in project_dir.rglob('*'):
            if file_path.is_file() and not self._is_ignored_file(file_path):
                file_count += 1

                # Detect tech stack
                if file_path.suffix in ['.py']:
                    tech_stack.add('python')
                elif file_path.suffix in ['.js', '.ts']:
                    tech_stack.add('javascript')
                elif file_path.suffix in ['.java']:
                    tech_stack.add('java')
                elif file_path.suffix in ['.go']:
                    tech_stack.add('go')

                # Count lines (approximate)
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        lines = f.readlines()
                        loc_count += len([line for line in lines if line.strip()])
                except:
                    pass

        context.tech_stack = list(tech_stack)
        context.files_analyzed = file_count
        context.loc_estimated = loc_count

        logger.info(f"📊 Basic project analysis: {file_count} files, {loc_count} LOC, tech: {list(tech_stack)}")
        return context

    def _classify_project_type(self, context: ProjectContext) -> ProjectType:
        """Classify project type based on tech stack"""
        tech_stack = set(context.tech_stack)

        if 'python' in tech_stack and any(x in ['tensorflow', 'pytorch', 'sklearn'] for x in context.tech_stack):
            return ProjectType.ML_AI
        elif 'go' in tech_stack or 'java' in tech_stack:
            return ProjectType.API_MICROSERVICES
        elif 'javascript' in tech_stack:
            return ProjectType.WEB_APP
        else:
            return ProjectType.WEB_APP  # Default

    def _is_ignored_file(self, file_path: Path) -> bool:
        """Check if file should be ignored"""
        ignore_patterns = [
            '__pycache__', '.git', 'node_modules', '.env',
            '*.pyc', '*.log', '*.tmp', '*.bak'
        ]

        path_str = str(file_path)
        return any(pattern in path_str for pattern in ignore_patterns)

    def get_cursor_stats(self) -> Dict[str, Any]:
        """Get system statistics"""
        return {
            "ai_model": "minimal_mode",
            "rules_count": 8,
            "knowledge_files": {"json": 5, "md": 3, "pdf": 4},
            "experience_entries": 0,
            "total_size_mb": 0.0,
            "ai_capabilities": [
                "Basic project analysis",
                "Rule selection",
                "Execution planning",
                "Code analysis"
            ]
        }
