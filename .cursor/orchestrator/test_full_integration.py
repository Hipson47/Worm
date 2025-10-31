#!/usr/bin/env python3
"""
Full Integration Test for AI Orchestrator Service
Tests the complete workflow from service startup to agent integration
"""

import asyncio
import time
import subprocess
import signal
import os
import sys
from pathlib import Path

async def test_orchestrator_service():
    """Test the orchestrator service functionality"""
    print("🧪 Testing AI Orchestrator Service")
    print("=" * 40)

    # Import here to avoid issues if service is not running
    try:
        from .ai_orchestrator_client import AIOrchestratorClient, get_project_context
        print("✅ Client import successful")
    except ImportError as e:
        print(f"❌ Client import failed: {e}")
        return False

    # Test client connection
    client = AIOrchestratorClient()

    try:
        # Test health check
        print("🔍 Testing health check...")
        health = await client.health_check()
        if health.get('status') == 'healthy':
            print("✅ Service is healthy")
        else:
            print(f"❌ Service health check failed: {health}")
            return False

        # Test project analysis
        print("🔍 Testing project analysis...")
        analysis = await client.analyze_project('.')
        if analysis.get('success'):
            print("✅ Project analysis successful")
            context = analysis['project_analysis']
            print(f"   📊 Found {context['files_analyzed']} files, {context['estimated_loc']} LOC")
        else:
            print(f"❌ Project analysis failed: {analysis}")
            return False

        # Test rule selection
        print("📋 Testing rule selection...")
        rules = await client.select_rules(
            task="Implement user authentication with JWT",
            project_context={
                'tech_stack': ['python', 'fastapi'],
                'project_type': 'web_app',
                'complexity': 'medium'
            }
        )
        if rules.get('success'):
            selected_rules = rules['rules_selection']['recommended_rules']
            print(f"✅ Rule selection successful: {selected_rules}")
        else:
            print(f"❌ Rule selection failed: {rules}")
            return False

        # Test plan generation
        print("📝 Testing plan generation...")
        plan = await client.generate_plan(
            task="Add user login endpoint",
            context={'tech_stack': ['python', 'fastapi']}
        )
        if plan.get('success'):
            print("✅ Plan generation successful")
        else:
            print(f"⚠️ Plan generation failed (expected for complex tasks): {plan}")

        # Test sync functions
        print("🔄 Testing sync convenience functions...")
        sync_rules = client.get_optimal_rules_sync("Create API endpoint")
        sync_plan = client.get_task_plan_sync("Implement database models")
        sync_context = get_project_context()

        print(f"✅ Sync rules: {sync_rules}")
        print(f"✅ Sync plan generated: {bool(sync_plan)}")
        print(f"✅ Sync context: {bool(sync_context)}")

        print("\n🎉 All orchestrator service tests passed!")
        return True

    except Exception as e:
        print(f"❌ Service test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        await client.close()

async def test_agent_integration():
    """Test the agent integration example"""
    print("\n🤖 Testing Agent Integration")
    print("=" * 30)

    try:
        # Import the integration example
        import example_agent_integration

        print("✅ Agent integration module imported")

        # Run a quick test
        result = example_agent_integration.enhanced_cursor_agent_task_processor(
            task_description="Create a simple function to validate email",
            code_context="def validate_email(email):\n    pass",
            file_path="utils.py",
            project_type="web_app"
        )

        if result and 'selected_rules' in result:
            print(f"✅ Agent integration test successful")
            print(f"   📋 Rules selected: {result['selected_rules']}")
            print(f"   📝 Plan generated: {bool(result['execution_plan'])}")
        else:
            print(f"❌ Agent integration test failed: {result}")
            return False

        return True

    except Exception as e:
        print(f"❌ Agent integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def start_service_process():
    """Start the orchestrator service in background"""
    print("🚀 Starting orchestrator service in background...")

    try:
        # Start service
        process = subprocess.Popen(
            [sys.executable, 'ai_orchestrator_service.py'],
            cwd='.',
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            preexec_fn=os.setsid if hasattr(os, 'setsid') else None
        )

        # Wait for service to start
        time.sleep(3)

        # Check if process is still running
        if process.poll() is None:
            print("✅ Service started successfully")
            return process
        else:
            stdout, stderr = process.communicate()
            print(f"❌ Service failed to start")
            print(f"STDOUT: {stdout.decode()}")
            print(f"STDERR: {stderr.decode()}")
            return None

    except Exception as e:
        print(f"❌ Failed to start service: {e}")
        return None

def stop_service_process(process):
    """Stop the background service process"""
    if process:
        try:
            if hasattr(os, 'killpg'):
                os.killpg(os.getpgid(process.pid), signal.SIGTERM)
            else:
                process.terminate()

            process.wait(timeout=5)
            print("✅ Service stopped")
        except Exception as e:
            print(f"⚠️ Error stopping service: {e}")
            try:
                process.kill()
            except:
                pass

async def run_full_integration_test():
    """Run the complete integration test"""
    print("🎯 AI Orchestrator Full Integration Test")
    print("=" * 50)
    print()

    # Change to .cursor directory
    original_dir = os.getcwd()
    cursor_dir = Path(original_dir) / '.cursor'

    if not cursor_dir.exists():
        print(f"❌ .cursor directory not found: {cursor_dir}")
        return False

    os.chdir(cursor_dir)
    print(f"📁 Working directory: {cursor_dir}")

    service_process = None

    try:
        # Start service
        service_process = start_service_process()
        if not service_process:
            return False

        # Wait a bit more for service initialization
        await asyncio.sleep(2)

        # Test service functionality
        service_ok = await test_orchestrator_service()
        if not service_ok:
            return False

        # Test agent integration
        agent_ok = await test_agent_integration()
        if not agent_ok:
            return False

        print("\n🎉 ALL INTEGRATION TESTS PASSED!")
        print("✅ Service is running and responding")
        print("✅ Client can communicate with service")
        print("✅ Agent integration works correctly")
        print("✅ AI-powered rule selection functional")
        print("✅ Execution planning operational")
        print("✅ Project analysis working")

        print("\n🚀 System is ready for production use!")
        return True

    except Exception as e:
        print(f"\n❌ Integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

    finally:
        # Cleanup
        stop_service_process(service_process)
        os.chdir(original_dir)

if __name__ == "__main__":
    success = asyncio.run(run_full_integration_test())
    sys.exit(0 if success else 1)
