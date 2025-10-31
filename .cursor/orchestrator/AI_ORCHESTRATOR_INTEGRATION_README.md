# 🤖 AI Orchestrator - Cursor Agent Integration

The **AI-Powered Universal Cursor Orchestrator** intelligently supervises the Cursor agent, dynamically adapting behavior by selecting optimal rules and execution strategies.

## 🎯 System Architecture

```
┌─────────────────┐    HTTP API    ┌──────────────────────┐
│  Cursor Agent   │◄─────────────►│ AI Orchestrator      │
│                 │               │ Service (Port 8765)  │
│ • Rules Engine  │               │                      │
│ • Task Analysis │               │ • AI Classification  │
│ • Code Generation│               │ • Rules Selection   │
│ • Quality Control│               │ • Plan Generation   │
└─────────────────┘               │ • Recommendations    │
                                  └──────────────────────┘
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

## 🚀 Quick Start

### 1. Start Orchestrator Service

```bash
cd .cursor/orchestrator

# Start service (default port 8765)
python ai_orchestrator_service.py

# Or with a custom port
python ai_orchestrator_service.py --port 8080
```

Service will be available at `http://localhost:8765`

### 2. Verify Service

```bash
# Health check
curl http://localhost:8765/

# Expected response:
{
  "status": "healthy",
  "timestamp": "2025-10-28T20:50:00.000Z",
  "version": "1.0.0",
  "ai_available": true
}
```

### 3. Integrate with Cursor Agent

In your rules file (e.g. `.cursor/rules/31_advanced_agent_steering.mdc`) add:

```python
# At the top of the rules file
from ai_orchestrator_client import select_optimal_rules, get_execution_plan, analyze_code_for_insights

# Example usage inside agent function
def enhance_task_execution(task_description, context):
    # Get optimal rules for the task
    optimal_rules = select_optimal_rules(
        task=task_description,
        current_file=context.get('file', ''),
        project_type=context.get('project_type', '')
    )

    # Get execution plan
    execution_plan = get_execution_plan(task_description)

    # Analyze code if provided
    if 'code' in context:
        insights = analyze_code_for_insights(
            code=context['code'],
            context=task_description
        )

    # Apply selected rules in optimal order
    result = apply_rules_in_order(optimal_rules, task_description, execution_plan)

    return result
```

## 📋 API Endpoints

### Core Endpoints

| Endpoint | Method | Description |
|----------|--------|------|
| `/` | GET | System health check |
| `/api/analyze-project` | POST | Analyze project structure |
| `/api/select-rules` | POST | Select optimal rules |
| `/api/generate-plan` | POST | Generate execution plan |
| `/api/get-recommendations` | POST | Recommendations for code/tasks |
| `/api/orchestrate-task` | POST | Full task orchestration |
| `/api/analyze-code` | POST | Source code analysis |
| `/api/get-context` | POST | Retrieve project context |

### API Usage Examples

#### Select Rules for a Task
```bash
curl -X POST http://localhost:8765/api/select-rules \
  -H "Content-Type: application/json" \
  -d '{
    "task": "Implement user authentication with JWT tokens",
    "project_context": {
      "tech_stack": ["python", "fastapi", "postgresql"],
      "project_type": "web_app",
      "complexity": "medium"
    },
    "current_rules": ["00_policy"]
  }'
```

**Response:**
```json
{
  "success": true,
  "rules_selection": {
    "recommended_rules": [
      "20_security_basics",
      "30_hybrid_moe_tot_reasoning",
      "31_advanced_agent_steering"
    ],
    "reasoning": "Authentication requires security focus with JWT validation",
    "priority_order": [
      "20_security_basics",
      "30_hybrid_moe_tot_reasoning",
      "31_advanced_agent_steering"
    ]
  }
}
```

#### Generate Execution Plan
```bash
curl -X POST http://localhost:8765/api/generate-plan \
  -H "Content-Type: application/json" \
  -d '{
    "task": "Add user registration API endpoint",
    "context": {
      "tech_stack": ["python", "fastapi"],
      "existing_endpoints": 5,
      "database": "postgresql"
    }
  }'
```

#### Analyze Project
```bash
curl -X POST http://localhost:8765/api/analyze-project \
  -H "Content-Type: application/json" \
  -d '{
    "project_path": "/path/to/project"
  }'
```

## 🛠️ Client for Cursor Agent

### Installation and Usage

```python
# Import in your rules file
from ai_orchestrator_client import (
    select_optimal_rules,
    get_execution_plan,
    analyze_code_for_insights,
    get_project_context
)

# Example implementation inside rules
def process_task_enhanced(task, context):
    # 1. Select optimal rules
    rules = select_optimal_rules(
        task=task.description,
        current_file=task.file_path,
        project_type=context.get('project_type')
    )

    # 2. Get execution plan
    plan = get_execution_plan(task.description)

    # 3. Analyze project context
    project_info = get_project_context()

    # 4. Apply insights
    if task.code:
        insights = analyze_code_for_insights(task.code, task.description)

    # 5. Execute task with selected rules
    return execute_with_rules(task, rules, plan, insights)
```

### Synchronous API (For Easier Integration)

```python
# All functions also have sync versions
from ai_orchestrator_client import (
    AIOrchestratorClient  # Async client
)

# Sync convenience functions
rules = select_optimal_rules(task)
plan = get_execution_plan(task)
insights = analyze_code_for_insights(code)
context = get_project_context()
```

## 🎛️ Rules Configuration

### How Rules Use the Orchestrator

1. **31_advanced_agent_steering.mdc** - Main integration
   - Dynamic reasoning strategy selection
   - Adaptation to task context
   - Optimized rules sequencing

2. **30_hybrid_moe_tot_reasoning.mdc** - AI-Powered Reasoning
   - ToT (Tree-of-Thought) planning
   - MoE (Mixture-of-Experts) allocation
   - Context-aware reasoning

3. **20_security_basics.mdc** - Security-First Approach
   - CWE checklist integration
   - Threat modeling automation
   - Compliance rule selection

### Example Implementation in Rules

```python
# .cursor/rules/31_advanced_agent_steering.mdc

def apply_cursor_agent_steering(task_context):
    """
    Enhanced agent steering with AI orchestration
    """

    # Get recommendations from the orchestrator
    optimal_rules = select_optimal_rules(
        task=task_context['description'],
        current_file=task_context.get('file'),
        project_type=task_context.get('project_type')
    )

    # Get execution strategy
    execution_strategy = get_execution_plan(
        task_context['description']
    )

    # Adapt agent behavior
    adapted_behavior = {
        'rules_sequence': optimal_rules,
        'execution_mode': execution_strategy.get('mode', 'balanced'),
        'quality_gates': execution_strategy.get('quality_checks', []),
        'fallback_strategies': execution_strategy.get('alternatives', [])
    }

    return adapted_behavior
```

## 🔧 Troubleshooting

### Problem: Service does not start
```
❌ Failed to initialize orchestrator: API key not configured
```

**Solution:**
1. Check `ai_config.json` - is the API key configured?
2. Run `python ai_simple_config.py setup` to configure keys

### Problem: Agent cannot connect to the service
```
ConnectionError: Connection refused
```

**Solution:**
1. Verify service is running: `curl http://localhost:8765/`
2. Check port: default 8765
3. Check firewall/antivirus

### Problem: Rules are not applied optimally
```
Warning: Using fallback rules selection
```

**Solution:**
1. Check service connectivity
2. Verify API key configuration
3. Check service logs for AI errors

## 📊 Metrics and Monitoring

### Health Check Response
```json
{
  "status": "healthy",
  "timestamp": "2025-10-28T20:50:00.000Z",
  "version": "1.0.0",
  "ai_available": true
}
```

### Service Logs
The service logs all operations:
- AI requests and responses
- Rule selections
- Plan generations
- Error conditions

### Performance
- **Response Time**: 2-5 seconds for AI operations
- **Throughput**: 10-20 requests/minute
- **Reliability**: Fallback modes for all operations

## 🔄 Integration Workflow

1. **Cursor Agent** receives a user task
2. **Agent** queries orchestrator for optimal rules
3. **Orchestrator** analyzes task and context
4. **AI** selects best rules and strategy
5. **Agent** applies selected rules in optimal order
6. **Orchestrator** monitors execution and recommends adjustments
7. **Agent** adapts in real time

## 🎯 Benefits for Cursor Agent

### Dynamic Adaptation
- Automatic adaptation to task type
- Context-aware rule selection
- Project-specific optimization

### Higher Quality
- AI-powered code analysis
- Security-first approach
- Comprehensive testing strategies

### Better Performance
- Optimized rule sequences
- Intelligent resource allocation
- Reduced error rates

### Continuous Learning
- Experience-based improvements
- Pattern recognition
- Adaptive strategies

---

**🚀 The system is now fully functional and ready to revolutionize Cursor agent work with intelligent orchestration!**
