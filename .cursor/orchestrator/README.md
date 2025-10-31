# 🤖 AI Orchestrator - Core System

**AI-Powered Universal Cursor Orchestrator** - intelligent supervision over the Cursor agent by dynamically selecting optimal strategies and execution rules.

## 📁 Folder Structure

```
.cursor/orchestrator/
├── 📄 ai_orchestrator.py              # Main AI orchestrator
├── 📄 ai_orchestrator_service.py      # HTTP API service (port 8765)
├── 📄 ai_orchestrator_client.py       # Client for agent integration
├── 📄 ai_simple_config.py             # Simple configuration system
├── 📄 ai_config.json                  # API keys configuration
├── 📄 AI_CONFIG_SIMPLE_README.md      # Config documentation
├── 📄 AI_ORCHESTRATOR_INTEGRATION_README.md  # Main documentation
├── 📄 start_orchestrator.sh           # Auto-start script
├── 📄 test_full_integration.py        # Full system tests
├── 📄 example_agent_integration.py    # Integration example
├── 📄 .ai_secure_gitignore            # Git ignore rules
└── 📄 README.md                       # This file
```

## 🚀 Quick Start

### 1. Configuration
```bash
# Go to orchestrator folder
cd .cursor/orchestrator

# Configure API keys
python ai_simple_config.py setup
```

### 2. Run
```bash
# Start the orchestrator service
./start_orchestrator.sh

# Or run manually
python ai_orchestrator_service.py
```

### 3. Verification
```bash
# Check if it's running
curl http://localhost:8765/

# Expected: {"status": "healthy", ...}
```

## 🎯 Main Components

### AIOrchestrator
- **File**: `ai_orchestrator.py`
- **Role**: Core AI engine for project analysis, agent allocation, and plan generation
- **Capabilities**: Project classification, strategy selection, cost optimization

### AIOrchestratorService
- **File**: `ai_orchestrator_service.py`
- **Role**: HTTP API for Cursor agent integration
- **Endpoints**: `/api/analyze-project`, `/api/select-rules`, `/api/generate-plan`, etc.
- **Port**: 8765 (default)

### AIOrchestratorClient
- **File**: `ai_orchestrator_client.py`
- **Role**: Python client for easy integration in Cursor rules
- **Methods**: `select_optimal_rules()`, `get_execution_plan()`, `analyze_code_for_insights()`

### AISimpleConfig
- **File**: `ai_simple_config.py`
- **Role**: Simple JSON configuration management
- **Security**: Optional encryption for sensitive data

## 🔧 Integration with Cursor Agent

### Automatic Activation
With `99_orchestrator_automation.mdc`, the orchestrator is **automatically enabled** for all tasks.

### Manual Integration
```python
# In your rules file (.mdc)
from pathlib import Path
import sys

# Add orchestrator path
orchestrator_path = Path(__file__).parent.parent / 'orchestrator'
sys.path.insert(0, str(orchestrator_path))

# Import the client
from ai_orchestrator_client import select_optimal_rules, get_execution_plan

# Use in code
def enhance_agent_behavior(task):
    optimal_rules = select_optimal_rules(task.description)
    plan = get_execution_plan(task.description)
    # ... further logic
```

## 📊 System Architecture

```
┌─────────────────┐    HTTP API    ┌──────────────────────┐
│  Cursor Agent   │◄─────────────►│ AI Orchestrator      │
│                 │               │ Service (Port 8765)  │
│ • Rules Engine  │               │                      │
│ • Task Analysis │               │ • AI Classification  │
│ • Code Generation│               │ • Rules Selection   │
│ • Quality Control│               │ • Plan Generation   │
└─────────────────┘               └──────────────────────┘
                                       │
                                       ▼
                              ┌──────────────────────┐
                              │   AI Orchestrator    │
                              │     Core Engine     │
                              │                      │
                              │ • Project Analysis  │
                              │ • Agent Allocation  │
                              │ • Execution Planning│
                              │ • Quality Assessment│
                              └──────────────────────┘
```

## 🛠️ Development and Testing

### Integration Tests
```bash
# Run full tests
python test_full_integration.py
```

### Integration Example
```bash
# See how to integrate the orchestrator
python example_agent_integration.py
```

### Debugging
```bash
# Check service logs
python ai_orchestrator_service.py --log-level DEBUG

# Test API manually
curl -X POST http://localhost:8765/api/select-rules \
  -H "Content-Type: application/json" \
  -d '{"task": "Implement user authentication"}'
```

## 🔒 Security

- **API Keys**: Stored in `ai_config.json` (do not commit!)
- **Git Ignore**: `.ai_secure_gitignore` controls sensitive files
- **Encryption**: Optional for sensitive data
- **Isolation**: All orchestrator files are isolated in this folder

## 📈 Metrics and Monitoring

### Key Metrics
- **Service Uptime**: Service availability
- **Task Supervision**: % of tasks supervised by orchestrator
- **Rule Selection Accuracy**: Accuracy of optimal rule selection
- **API Response Time**: API latency
- **Learning Effectiveness**: Effectiveness of learning system

### Health Monitoring
```bash
# Health check
curl http://localhost:8765/

# Detailed metrics
curl http://localhost:8765/api/analyze-project
```

## 🚨 Troubleshooting

### Service won't start
```
❌ Failed to initialize orchestrator: API key not configured
```
**Solution:**
```bash
cd .cursor/orchestrator
python ai_simple_config.py setup
```

### Agent cannot connect
```
ConnectionError: Connection refused
```
**Solution:**
```bash
# Verify service is running
curl http://localhost:8765/

# If not - start it
./start_orchestrator.sh
```

### Import errors
```
ImportError: No module named 'ai_orchestrator_client'
```
**Solution:** Ensure the path is correctly added in rules:
```python
orchestrator_path = Path(__file__).parent.parent / 'orchestrator'
sys.path.insert(0, str(orchestrator_path))
```

## 📚 Documentation

- **[Configuration](AI_CONFIG_SIMPLE_README.md)** - how to configure API keys
- **[Integration](AI_ORCHESTRATOR_INTEGRATION_README.md)** - detailed agent integration
- **[Rules Automation](../rules/99_orchestrator_automation.mdc)** - automatic activation in the system

## 🔄 Updates

The system is designed for continuous learning:
- **Automatic optimizations** of execution strategies
- **Learning from past tasks** and outcomes
- **Adaptation to context** of project and user

---

**🎯 The Orchestrator is a key component of the Cursor Agent system - providing intelligent supervision and optimization of all operations.**

**Status**: ✅ **OPERATIONAL** - System ready for production use.
