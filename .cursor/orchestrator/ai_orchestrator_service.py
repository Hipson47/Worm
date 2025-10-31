#!/usr/bin/env python3
"""
AI Orchestrator Service - MCP Integration for Cursor Agent
Runs an HTTP server to communicate with the Cursor agent
"""

import asyncio
import json
import logging
from typing import Dict, Any, Optional
from datetime import datetime
from pathlib import Path

from aiohttp import web, ClientError
from .ai_orchestrator import AIOrchestrator
from .ai_simple_config import AISimpleConfig

# Logging configuration - stderr only for MCP compatibility
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stderr  # stderr only, stdout reserved for JSON-RPC
)
logger = logging.getLogger(__name__)

class AIOrchestratorService:
    """HTTP server for AI Orchestrator - MCP Cursor integration"""

    def __init__(self, port: int = 8765):
        self.port = port
        self.orchestrator = None
        self.config = AISimpleConfig(".")
        self.app = web.Application()
        self.runner = None
        self.site = None

        # Setup routes
        self._setup_routes()

    def _setup_routes(self):
        """Configure API endpoints"""
        self.app.router.add_get('/', self.health_check)
        self.app.router.add_post('/api/analyze-project', self.analyze_project)
        self.app.router.add_post('/api/select-rules', self.select_rules)
        self.app.router.add_post('/api/generate-plan', self.generate_plan)
        self.app.router.add_post('/api/get-recommendations', self.get_recommendations)
        self.app.router.add_post('/api/orchestrate-task', self.orchestrate_task)
        self.app.router.add_post('/api/analyze-code', self.analyze_code)
        self.app.router.add_post('/api/get-context', self.get_context)

    async def health_check(self, request):
        """System health endpoint"""
        return web.json_response({
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'version': '1.0.0',
            'ai_available': bool(self.config.get_openai_key())
        })

    async def analyze_project(self, request):
        """Project analysis for Cursor agent"""
        try:
            data = await request.json()
            project_path = data.get('project_path', '.')

            # Initialize orchestrator if needed
            if not self.orchestrator:
                self.orchestrator = AIOrchestrator()

            # Perform analysis
            context = self.orchestrator._basic_project_analysis(project_path)

            # AI-driven classification if available
            try:
                project_type_result = await self.orchestrator._ai_classify_project_type(context)
                project_type = self._normalize_project_type(project_type_result.get('type', 'web_app'))
            except Exception:
                project_type = 'web_app'

            return web.json_response({
                'success': True,
                'project_analysis': {
                    'tech_stack': context.tech_stack,
                    'architecture': context.architecture,
                    'domain': context.domain,
                    'scale': context.scale,
                    'project_type': project_type,
                    'files_analyzed': context.files_analyzed,
                    'estimated_loc': context.loc_estimated
                },
                'confidence': project_type_result.get('confidence', 0.8) if 'project_type_result' in locals() else 0.8
            })

        except Exception as e:
            logger.error(f"Project analysis failed: {e}")
            return web.json_response({
                'success': False,
                'error': str(e)
            }, status=500)

    async def select_rules(self, request):
        """Wybór odpowiednich rules dla zadania"""
        try:
            data = await request.json()
            task_description = data.get('task', '')
            project_context = data.get('project_context', {})
            current_rules = data.get('current_rules', [])

            # Inicjalizuj orchestrator jeśli potrzeba
            if not self.orchestrator:
                self.orchestrator = AIOrchestrator()

            # Analiza zadania i kontekstu
            analysis_prompt = f"""
Przeanalizuj zadanie i wybierz odpowiednie rules z dostępnych:

ZADANIE: {task_description}

KONTEKST PROJEKTU:
- Tech Stack: {project_context.get('tech_stack', [])}
- Project Type: {project_context.get('project_type', 'unknown')}
- Complexity: {project_context.get('complexity', 'medium')}

DOSTĘPNE RULES:
- 00_policy: Bezpieczeństwo i polityka
- 20_security_basics: CWE checklist, threat modeling
- 30_hybrid_moe_tot_reasoning: MoE system, ToT reasoning
- 31_advanced_agent_steering: Prompting, MCP integration
- 40_docker_basics: Konteneryzacja, Docker best practices
- 50_universal_project_orchestrator: Architektura projektów
- 55_universal_project_patterns: Wzorce projektowe
- 70_learning_system: System uczenia się

OBECNE RULES: {', '.join(current_rules)}

Wybierz 3-5 NAJWAŻNIEJSZYCH rules dla tego zadania.
Odpowiedz w formacie JSON z kluczami:
- recommended_rules: lista nazw rules
- reasoning: uzasadnienie wyboru
- priority_order: kolejność zastosowania
"""

            # AI wybór rules
            try:
                ai_client = await self.orchestrator._get_ai_client()
                async with ai_client:
                    ai_response = await ai_client.ask(analysis_prompt)
                rules_data = json.loads(ai_response)
            except Exception as e:
                logger.warning(f"AI rules selection failed: {e}, using fallback")
                # Fallback - proste reguły na podstawie słów kluczowych
                rules_data = self._fallback_rules_selection(task_description, project_context)

            return web.json_response({
                'success': True,
                'rules_selection': rules_data,
                'task': task_description,
                'context': project_context
            })

        except Exception as e:
            logger.error(f"Rules selection failed: {e}")
            return web.json_response({
                'success': False,
                'error': str(e)
            }, status=500)

    def _fallback_rules_selection(self, task: str, context: dict) -> dict:
        """Fallback wybór rules na podstawie analizy tekstu"""
        task_lower = task.lower()
        rules = []

        # Bezpieczeństwo zawsze pierwsze
        if any(word in task_lower for word in ['security', 'bezpieczeństwo', 'auth', 'login']):
            rules.append('20_security_basics')

        # Architektura i planowanie
        if any(word in task_lower for word in ['architecture', 'architektura', 'design', 'plan']):
            rules.extend(['50_universal_project_orchestrator', '55_universal_project_patterns'])

        # AI and reasoning
        if any(word in task_lower for word in ['ai', 'analyze', 'analiz', 'reasoning']):
            rules.append('30_hybrid_moe_tot_reasoning')

        # Docker and deployment
        if any(word in task_lower for word in ['docker', 'container', 'deploy', 'production']):
            rules.append('40_docker_basics')

        # Default rules
        if not rules:
            rules = ['30_hybrid_moe_tot_reasoning', '31_advanced_agent_steering', '00_policy']

        return {
            'recommended_rules': rules,
            'reasoning': 'Fallback selection based on task keywords',
            'priority_order': rules
        }

    async def generate_plan(self, request):
        """Generate execution plan for the agent"""
        try:
            data = await request.json()
            task = data.get('task', '')
            context = data.get('context', {})

            # Initialize orchestrator if needed
            if not self.orchestrator:
                self.orchestrator = AIOrchestrator()

            # Mock context for AI
            mock_context = type('MockContext', (), {
                'tech_stack': context.get('tech_stack', ['python']),
                'architecture': context.get('architecture', 'monolith'),
                'domain': context.get('domain', 'web'),
                'scale': context.get('scale', 'small'),
                'compliance': context.get('compliance', []),
                'files_analyzed': context.get('files_analyzed', 10),
                'loc_estimated': context.get('loc_estimated', 1000)
            })()

            # Mock metrics
            mock_metrics = type('MockMetrics', (), {
                'quality_score': 0.85,
                'success_rate': 0.9,
                'time_spent': 0
            })()

            # Generate plan
            try:
                plan_result = await self.orchestrator._ai_generate_execution_plan(
                    type('MockType', (), {'value': 'web_app'})(),  # Mock project type
                    mock_context,
                    type('MockAllocation', (), {})()  # Mock allocation
                )
            except Exception as e:
                logger.warning(f"AI plan generation failed: {e}")
                plan_result = {
                    'plan': {
                        'Planning': {'tasks': ['Analyze requirements'], 'estimated_hours': 2},
                        'Implementation': {'tasks': ['Write code'], 'estimated_hours': 4},
                        'Testing': {'tasks': ['Run tests'], 'estimated_hours': 2}
                    },
                    'reasoning': 'Fallback plan generation'
                }

            return web.json_response({
                'success': True,
                'execution_plan': plan_result,
                'task': task
            })

        except Exception as e:
            logger.error(f"Plan generation failed: {e}")
            return web.json_response({
                'success': False,
                'error': str(e)
            }, status=500)

    async def get_recommendations(self, request):
        """Pobieranie rekomendacji dla agenta"""
        try:
            data = await request.json()
            code_context = data.get('code', '')
            task_context = data.get('task', '')

            # Inicjalizuj orchestrator jeśli potrzeba
            if not self.orchestrator:
                self.orchestrator = AIOrchestrator()

            # Mock context i metrics dla rekomendacji
            mock_context = type('MockContext', (), {'tech_stack': ['python'], 'compliance': []})()
            mock_metrics = type('MockMetrics', (), {'quality_score': 0.8, 'success_rate': 0.85, 'time_spent': 100, 'errors_count': 0})()

            try:
                rec_result = await self.orchestrator._ai_generate_recommendations(mock_context, mock_metrics)
            except Exception as e:
                logger.warning(f"AI recommendations failed: {e}")
                rec_result = {
                    'recommendations': [
                        'Follow established coding standards',
                        'Add comprehensive error handling',
                        'Include input validation'
                    ]
                }

            return web.json_response({
                'success': True,
                'recommendations': rec_result,
                'context': {'code_length': len(code_context), 'task': task_context[:100]}
            })

        except Exception as e:
            logger.error(f"Recommendations failed: {e}")
            return web.json_response({
                'success': False,
                'error': str(e)
            }, status=500)

    async def orchestrate_task(self, request):
        """Full task orchestration for the agent"""
        try:
            data = await request.json()
            task_description = data.get('task', '')
            project_path = data.get('project_path', '.')

            # Initialize orchestrator if needed
            if not self.orchestrator:
                self.orchestrator = AIOrchestrator()

            # Run orchestration
            result = await self.orchestrator.orchestrate_project(project_path)

            return web.json_response({
                'success': True,
                'orchestration_result': {
                    'project_type': result.project_type.value,
                    'agent_allocation': {
                        'planner': result.agent_allocation.planner,
                        'reasoner': result.agent_allocation.reasoner,
                        'implementer': result.agent_allocation.implementer,
                        'tester': result.agent_allocation.tester
                    },
                    'execution_plan_phases': len(result.execution_plan),
                    'quality_score': result.metrics.quality_score,
                    'recommendations_count': len(result.recommendations)
                },
                'ai_reasoning': result.ai_reasoning[:500] if result.ai_reasoning else ''
            })

        except Exception as e:
            logger.error(f"Task orchestration failed: {e}")
            return web.json_response({
                'success': False,
                'error': str(e)
            }, status=500)

    async def analyze_code(self, request):
        """Source code analysis for the agent"""
        try:
            data = await request.json()
            code = data.get('code', '')
            language = data.get('language', 'python')
            task = data.get('task', '')

            # Simple code analysis
            analysis = {
                'language': language,
                'lines': len(code.split('\n')),
                'characters': len(code),
                'functions': code.count('def ') if language == 'python' else 0,
                'classes': code.count('class ') if language == 'python' else 0,
                'imports': code.count('import ') if language == 'python' else 0
            }

            # Recommendations based on analysis
            recommendations = []
            if analysis['lines'] > 100:
                recommendations.append('Consider breaking into smaller functions')
            if analysis['functions'] > 10:
                recommendations.append('High function count - consider modularization')
            if analysis['imports'] > 15:
                recommendations.append('Many imports - review dependencies')

            return web.json_response({
                'success': True,
                'code_analysis': analysis,
                'recommendations': recommendations,
                'task_context': task
            })

        except Exception as e:
            logger.error(f"Code analysis failed: {e}")
            return web.json_response({
                'success': False,
                'error': str(e)
            }, status=500)

    async def get_context(self, request):
        """Get project context for the agent"""
        try:
            data = await request.json()
            project_path = data.get('project_path', '.')

            # Initialize orchestrator if needed
            if not self.orchestrator:
                self.orchestrator = AIOrchestrator()

            context = self.orchestrator._basic_project_analysis(project_path)

            return web.json_response({
                'success': True,
                'project_context': {
                    'tech_stack': context.tech_stack,
                    'architecture': context.architecture,
                    'domain': context.domain,
                    'scale': context.scale,
                    'files': context.files_analyzed,
                    'estimated_loc': context.loc_estimated
                }
            })

        except Exception as e:
            logger.error(f"Context retrieval failed: {e}")
            return web.json_response({
                'success': False,
                'error': str(e)
            }, status=500)

    def _normalize_project_type(self, type_str: str) -> str:
        """Normalize project type to enum format"""
        type_map = {
            'WEB_APP': 'web_app',
            'API_MICROSERVICES': 'api_microservices',
            'ML_AI': 'ml_ai',
            'MOBILE_APP': 'mobile_app',
            'IOT_EMBEDDED': 'iot_embedded',
            'ENTERPRISE_SYSTEM': 'enterprise_system'
        }
        return type_map.get(type_str.upper(), 'web_app')

    async def start(self):
        """Uruchomienie serwera"""
        logger.info(f"🚀 Starting AI Orchestrator Service on port {self.port}")

        # Inicjalizuj orchestrator
        try:
            self.orchestrator = AIOrchestrator()
            logger.info("✅ AI Orchestrator initialized")
        except Exception as e:
            logger.error(f"❌ Failed to initialize orchestrator: {e}")
            return False

        # Uruchom serwer
        self.runner = web.AppRunner(self.app)
        await self.runner.setup()
        self.site = web.TCPSite(self.runner, 'localhost', self.port)
        await self.site.start()

        logger.info(f"🎯 AI Orchestrator Service ready at http://localhost:{self.port}")
        logger.info("📋 Available endpoints:")
        logger.info("  GET  / - Health check")
        logger.info("  POST /api/analyze-project - Project analysis")
        logger.info("  POST /api/select-rules - Rules selection")
        logger.info("  POST /api/generate-plan - Plan generation")
        logger.info("  POST /api/get-recommendations - Recommendations")
        logger.info("  POST /api/orchestrate-task - Full orchestration")
        logger.info("  POST /api/analyze-code - Code analysis")
        logger.info("  POST /api/get-context - Project context")

        return True

    async def stop(self):
        """Zatrzymanie serwera"""
        logger.info("🛑 Stopping AI Orchestrator Service")
        if self.site:
            await self.site.stop()
        if self.runner:
            await self.runner.cleanup()
        logger.info("✅ AI Orchestrator Service stopped")


async def main():
    """Główna funkcja"""
    import argparse

    parser = argparse.ArgumentParser(description="AI Orchestrator Service for Cursor Agent")
    parser.add_argument('--port', type=int, default=8765, help='Port to run the service on')
    parser.add_argument('--log-level', default='INFO', choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'])

    args = parser.parse_args()

    # Ustaw poziom logowania
    logging.getLogger().setLevel(getattr(logging, args.log_level))

    # Uruchom serwis
    service = AIOrchestratorService(port=args.port)

    try:
        success = await service.start()
        if not success:
            return

        # Trzymaj serwis uruchomiony
        logger.info("🔄 Service running... Press Ctrl+C to stop")

        # Setup graceful shutdown
        def signal_handler(signum, frame):
            logger.info("📴 Shutdown signal received")
            asyncio.create_task(service.stop())

        import signal
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)

        # Keep running
        while True:
            await asyncio.sleep(1)

    except KeyboardInterrupt:
        logger.info("🛑 Keyboard interrupt received")
    except Exception as e:
        logger.error(f"❌ Service error: {e}")
    finally:
        await service.stop()


if __name__ == "__main__":
    asyncio.run(main())
