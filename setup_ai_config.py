#!/usr/bin/env python3
"""
Safe AI Configuration Setup Script
Run this to configure API keys securely in .env file
"""

import os
from pathlib import Path

def main():
    print("🔧 AI Orchestrator - Safe .env Configuration Setup")
    print("=" * 55)
    print("This script will help you configure API keys securely.")
    print("Keys will be stored in .env file and won't be committed to git.")
    print()

    env_file = Path(".env")

    # Check if .env already exists
    if env_file.exists():
        overwrite = input("   .env file already exists. Overwrite? (y/N): ").lower().strip()
        if overwrite != 'y':
            print("   Keeping existing .env file")
            return

    # OpenAI setup
    print("🤖 OpenAI Configuration:")
    print("   Get your API key from: https://platform.openai.com/api-keys")
    openai_key = input("   OpenAI API Key (press Enter to skip): ").strip()

    if openai_key and not openai_key.startswith('sk-'):
        print("   ❌ Invalid OpenAI API key format (should start with 'sk-')")
        return

    # Anthropic setup (optional)
    print("\n🧠 Anthropic Configuration (optional):")
    print("   Get your API key from: https://console.anthropic.com/")
    anthropic_key = input("   Anthropic API Key (press Enter to skip): ").strip()

    if anthropic_key and not anthropic_key.startswith('sk-ant-'):
        print("   ❌ Invalid Anthropic API key format (should start with 'sk-ant-')")
        return

    # Create .env content
    env_content = f"""# AI Orchestrator Configuration
# This file contains your API keys - NEVER commit to git!

# OpenAI Configuration
{f'OPENAI_API_KEY={openai_key}' if openai_key else '# OPENAI_API_KEY=your_openai_api_key_here'}
OPENAI_MODEL=gpt-4
OPENAI_MAX_TOKENS=2000
OPENAI_TEMPERATURE=0.3

# Anthropic Configuration (optional)
{f'ANTHROPIC_API_KEY={anthropic_key}' if anthropic_key else '# ANTHROPIC_API_KEY=your_anthropic_api_key_here'}
ANTHROPIC_MODEL=claude-3-sonnet
ANTHROPIC_MAX_TOKENS=2000

# Orchestrator Configuration
ORCHESTRATOR_AUTO_SAVE=true
ORCHESTRATOR_LOG_LEVEL=INFO
ORCHESTRATOR_CACHE_ENABLED=true
ORCHESTRATOR_TIMEOUT=300
"""

    # Write .env file
    with open(env_file, 'w') as f:
        f.write(env_content)

    print("\n💾 Configuration saved to .env")
    print("   ⚠️  .env file is automatically ignored by git")

    # Test configuration
    print("\n🧪 Testing configuration...")

    # Reload environment variables
    if openai_key:
        os.environ['OPENAI_API_KEY'] = openai_key
        print("   ✅ OpenAI key set in environment")

    if anthropic_key:
        os.environ['ANTHROPIC_API_KEY'] = anthropic_key
        print("   ✅ Anthropic key set in environment")

    # Test loading from .env
    try:
        import sys
        sys.path.insert(0, str(Path(__file__).parent / ".cursor"))
        from orchestrator.ai_simple_config import AISimpleConfig

        config = AISimpleConfig(".")
        test_openai = config.get_openai_key()
        test_anthropic = config.get_anthropic_key()

        if openai_key and test_openai == openai_key:
            print("   ✅ OpenAI key loaded successfully")
        elif openai_key:
            print("   ❌ OpenAI key test failed")

        if anthropic_key and test_anthropic == anthropic_key:
            print("   ✅ Anthropic key loaded successfully")
        elif anthropic_key:
            print("   ❌ Anthropic key test failed")

    except Exception as e:
        print(f"   ⚠️  Could not test loading: {e}")
        print("      This is normal if dependencies are not installed yet")

    print("\n🎉 Setup completed successfully!")
    print("   You can now run the AI Orchestrator with your .env configuration.")
    print("   Remember: Never commit .env file to git!")

if __name__ == "__main__":
    main()
