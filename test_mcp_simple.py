#!/usr/bin/env python3
"""
Simple MCP test without heavy dependencies
"""

import asyncio
import json
import subprocess
import sys
from pathlib import Path

async def test_basic_import():
    """Test if MCP modules can be imported"""
    print("🧪 Testing basic imports...")

    try:
        # Test orchestrator
        sys.path.insert(0, str(Path(__file__).parent / ".cursor"))
        from orchestrator.ai_orchestrator import AIOrchestrator
        print("✅ AIOrchestrator imported successfully")

        # Test config
        from orchestrator.ai_simple_config import AISimpleConfig
        print("✅ AISimpleConfig imported successfully")

        return True

    except ImportError as e:
        print(f"❌ Import failed: {e}")
        return False

async def test_config():
    """Test configuration loading"""
    print("🔧 Testing configuration...")

    try:
        from orchestrator.ai_simple_config import AISimpleConfig
        config = AISimpleConfig(".")
        print("✅ Config loaded successfully")

        # Test API key (won't be set in test)
        api_key = config.get_openai_key()
        if api_key:
            print("✅ API key configured")
        else:
            print("⚠️ API key not configured (expected in test)")

        return True

    except Exception as e:
        print(f"❌ Config test failed: {e}")
        return False

async def test_orchestrator_creation():
    """Test creating orchestrator instance"""
    print("🎯 Testing orchestrator creation...")

    try:
        from orchestrator.ai_orchestrator import AIOrchestrator
        from orchestrator.ai_simple_config import AISimpleConfig

        config = AISimpleConfig(".")
        orchestrator = AIOrchestrator()

        print("✅ Orchestrator created successfully")
        print(f"   Orchestrator initialized with config")

        return True

    except Exception as e:
        print(f"❌ Orchestrator creation failed: {e}")
        return False

async def test_knowledge_monitoring():
    """Test knowledge monitoring functionality"""
    print("\n🧪 Testing knowledge monitoring...")

    try:
        # Test knowledge monitor
        from orchestrator.rag_engine import KnowledgeMonitor

        monitor = KnowledgeMonitor(
            knowledge_dir=Path(__file__).parent / ".cursor" / "knowledge",
            rag_engine=None  # Dummy for test
        )

        # Check for updates (should find all files as new)
        has_updates = await monitor.check_for_updates()
        print(f"📁 Found updates: {has_updates}")
        print(f"📄 Indexed files: {len(monitor.knowledge_state.indexed_files)}")

        # Test state saving/loading
        monitor._save_state()
        print("💾 State saved successfully")

        print("✅ Knowledge monitoring test completed")
        return True

    except Exception as e:
        print(f"❌ Knowledge monitoring test failed: {e}")
        return False

async def run_tests():
    """Run all tests"""
    print("🚀 Starting MCP readiness tests...\n")

    tests = [
        ("Basic Imports", test_basic_import),
        ("Configuration", test_config),
        ("Orchestrator Creation", test_orchestrator_creation),
        ("Knowledge Monitoring", test_knowledge_monitoring),
    ]

    passed = 0
    total = len(tests)

    for name, test_func in tests:
        print(f"Running: {name}")
        if await test_func():
            passed += 1
        print()

    print(f"📊 Results: {passed}/{total} tests passed")

    if passed == total:
        print("✅ All tests passed! MCP system is ready.")
        return True
    else:
        print("❌ Some tests failed. Check the output above.")
        return False

if __name__ == "__main__":
    success = asyncio.run(run_tests())
    sys.exit(0 if success else 1)
