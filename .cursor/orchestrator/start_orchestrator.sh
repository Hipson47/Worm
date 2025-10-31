#!/bin/bash

# AI Orchestrator Service Launcher
# Automatically starts the orchestrator service with configuration

echo "🤖 AI Orchestrator Service Launcher"
echo "===================================="

# Verify current directory
if [ ! -f "ai_orchestrator_service.py" ]; then
    echo "❌ Error: Run from .cursor directory"
    echo "Usage: cd .cursor && ./start_orchestrator.sh"
    exit 1
fi

# Check configuration presence
if [ ! -f "ai_config.json" ]; then
    echo "⚠️  Config file not found. Running setup..."
    python ai_simple_config.py setup
fi

# Validate configuration
echo "🔍 Checking configuration..."
python -c "
from ai_simple_config import AISimpleConfig
config = AISimpleConfig('.')
if not config.get_openai_key():
    print('❌ OpenAI API key not configured')
    exit(1)
print('✅ Configuration OK')
"

if [ $? -ne 0 ]; then
    echo "❌ Configuration check failed. Run: python ai_simple_config.py setup"
    exit 1
fi

# Start service
echo "🚀 Starting AI Orchestrator Service..."
echo "📍 Service URL: http://localhost:8765"
echo "🛑 Press Ctrl+C to stop"
echo ""

cd /mnt/d/github/testy/AiBook/.cursor && PYTHONPATH=/mnt/d/github/testy/AiBook/.cursor python -m orchestrator.ai_orchestrator_service
