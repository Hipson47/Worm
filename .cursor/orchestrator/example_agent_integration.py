#!/usr/bin/env python3
"""
Example: How Cursor Agent can integrate with AI Orchestrator

This example shows how to enhance Cursor Agent capabilities
by integrating with the AI Orchestrator Service.
"""

from .ai_orchestrator_client import (
    select_optimal_rules,
    get_execution_plan,
    analyze_code_for_insights,
    get_project_context
)

def enhanced_cursor_agent_task_processor(task_description: str,
                                       code_context: str = "",
                                       file_path: str = "",
                                       project_type: str = ""):
    """
    Enhanced task processor that uses AI Orchestrator for optimal rule selection
    and execution planning.

    Args:
        task_description: Description of the task to perform
        code_context: Current code being worked on
        file_path: Path to the current file
        project_type: Type of project (web_app, api, ml, etc.)
    """

    print(f"🎯 Processing task: {task_description}")
    print("=" * 60)

    # 1. Get optimal rules for this task
    print("📋 Step 1: Selecting optimal rules...")
    optimal_rules = select_optimal_rules(
        task=task_description,
        current_file=file_path,
        project_type=project_type
    )

    print(f"✅ Selected rules: {', '.join(optimal_rules)}")
    print()

    # 2. Get execution plan
    print("📝 Step 2: Generating execution plan...")
    execution_plan = get_execution_plan(task_description)

    if execution_plan and 'plan' in execution_plan:
        print("✅ Execution plan generated:")
        plan = execution_plan['plan']
        for phase_name, phase_data in plan.items():
            tasks = phase_data.get('tasks', [])
            estimated_hours = phase_data.get('estimated_hours', 'N/A')
            print(f"   • {phase_name}: {len(tasks)} tasks (~{estimated_hours}h)")
    else:
        print("⚠️  Using fallback execution plan")
    print()

    # 3. Analyze code if provided
    if code_context:
        print("🔍 Step 3: Analyzing code context...")
        code_insights = analyze_code_for_insights(code_context, task_description)

        if code_insights:
            print("💡 Code insights:")
            for insight in code_insights:
                print(f"   • {insight}")
        else:
            print("ℹ️  No specific code insights generated")
        print()

    # 4. Get project context
    print("🌐 Step 4: Gathering project context...")
    project_info = get_project_context()

    if project_info:
        print("📊 Project context:")
        print(f"   • Tech Stack: {', '.join(project_info.get('tech_stack', []))}")
        print(f"   • Architecture: {project_info.get('architecture', 'unknown')}")
        print(f"   • Scale: {project_info.get('scale', 'unknown')}")
        print(f"   • Files: {project_info.get('files', 0)}")
    else:
        print("⚠️  Could not retrieve project context")
    print()

    # 5. Simulate rule application
    print("🚀 Step 5: Applying selected rules...")

    results = {
        'task': task_description,
        'selected_rules': optimal_rules,
        'execution_plan': execution_plan,
        'code_insights': code_insights if code_context else [],
        'project_context': project_info,
        'applied_rules': []
    }

    # Simulate applying each rule
    for rule_name in optimal_rules:
        print(f"   • Applying {rule_name}...")

        # Simulate rule application logic
        rule_result = apply_simulated_rule(rule_name, task_description, code_context)
        results['applied_rules'].append({
            'rule': rule_name,
            'result': rule_result
        })

        print(f"     ✅ {rule_result}")

    print()
    print("🎉 Task processing completed!")
    return results

def apply_simulated_rule(rule_name: str, task: str, code: str) -> str:
    """
    Simulate applying a specific rule to the task.
    In real implementation, this would call actual rule logic.
    """
    rule_actions = {
        '00_policy': 'Applied security and compliance checks',
        '20_security_basics': 'Implemented CWE security best practices',
        '30_hybrid_moe_tot_reasoning': 'Applied AI-powered reasoning and planning',
        '31_advanced_agent_steering': 'Optimized agent behavior and rule sequencing',
        '40_docker_basics': 'Configured containerization and deployment',
        '50_universal_project_orchestrator': 'Applied project architecture patterns',
        '55_universal_project_patterns': 'Implemented design patterns and best practices',
        '70_learning_system': 'Integrated learning and adaptation mechanisms'
    }

    return rule_actions.get(rule_name, f'Applied {rule_name} enhancements')

def demo_enhanced_agent():
    """Demonstrate the enhanced agent capabilities"""

    print("🤖 Enhanced Cursor Agent Demo")
    print("=============================")
    print()

    # Example 1: API Development Task
    print("📋 Example 1: API Development Task")
    result1 = enhanced_cursor_agent_task_processor(
        task_description="Implement user authentication API with JWT tokens and password hashing",
        code_context="",
        file_path="auth.py",
        project_type="web_app"
    )
    print()

    # Example 2: Database Migration Task
    print("📋 Example 2: Database Migration Task")
    result2 = enhanced_cursor_agent_task_processor(
        task_description="Create database migration for user roles table with proper constraints",
        code_context="class UserRole:\n    id = Column(Integer, primary_key=True)\n    name = Column(String(50), unique=True)",
        file_path="models.py",
        project_type="api"
    )
    print()

    # Example 3: Security Enhancement Task
    print("📋 Example 3: Security Enhancement Task")
    result3 = enhanced_cursor_agent_task_processor(
        task_description="Add input validation and SQL injection protection to user registration endpoint",
        code_context="def register_user(username, password, email):\n    # TODO: Add validation",
        file_path="auth_controller.py",
        project_type="web_app"
    )
    print()

    print("🎯 Demo completed! The enhanced agent can now:")
    print("   • Dynamically select optimal rules for each task")
    print("   • Generate AI-powered execution plans")
    print("   • Analyze code for insights and improvements")
    print("   • Adapt behavior based on project context")
    print("   • Apply rules in optimal sequences")

if __name__ == "__main__":
    demo_enhanced_agent()
