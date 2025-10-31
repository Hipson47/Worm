#!/usr/bin/env python3
"""
Simple and safe config for AI Orchestrator
Uses .env files only (industry standard)
"""

import os
from pathlib import Path
from typing import Dict, Any, Optional

try:
    from dotenv import load_dotenv
    DOTENV_AVAILABLE = True
except ImportError:
    DOTENV_AVAILABLE = False

class AISimpleConfig:
    """Simple config for AI Orchestrator - .env only approach"""

    def __init__(self, config_dir: str = "."):
        self.config_dir = Path(config_dir)

        # Load .env file only (required)
        if DOTENV_AVAILABLE:
            load_dotenv()
        else:
            raise ImportError("python-dotenv is required for .env configuration")

        # Validate that .env exists
        env_path = Path(".env")
        if not env_path.exists():
            raise FileNotFoundError(".env file is required but not found. Run 'python setup_ai_config.py' first.")

        # No fallback config loading - only .env is supported

    # No JSON config loading - only .env is supported

    def get_openai_key(self) -> Optional[str]:
        """Get OpenAI API key from .env only"""
        env_key = os.getenv("OPENAI_API_KEY")
        return env_key.strip() if env_key and env_key.strip() else None

    def get_anthropic_key(self) -> Optional[str]:
        """Get Anthropic API key from .env only"""
        env_key = os.getenv("ANTHROPIC_API_KEY")
        return env_key.strip() if env_key and env_key.strip() else None

    def get_openai_config(self) -> Dict[str, Any]:
        """Get full OpenAI configuration from .env"""
        return {
            "api_key": self.get_openai_key(),
            "model": os.getenv("OPENAI_MODEL", "gpt-4"),
            "max_tokens": int(os.getenv("OPENAI_MAX_TOKENS", "2000")),
            "temperature": float(os.getenv("OPENAI_TEMPERATURE", "0.3"))
        }

    def get_anthropic_config(self) -> Dict[str, Any]:
        """Get full Anthropic configuration from .env"""
        return {
            "api_key": self.get_anthropic_key(),
            "model": os.getenv("ANTHROPIC_MODEL", "claude-3-sonnet"),
            "max_tokens": int(os.getenv("ANTHROPIC_MAX_TOKENS", "2000"))
        }

    def get_orchestrator_config(self) -> Dict[str, Any]:
        """Get orchestrator configuration from .env"""
        return {
            "auto_save": os.getenv("ORCHESTRATOR_AUTO_SAVE", "true").lower() == "true",
            "log_level": os.getenv("ORCHESTRATOR_LOG_LEVEL", "INFO"),
            "cache_enabled": os.getenv("ORCHESTRATOR_CACHE_ENABLED", "true").lower() == "true",
            "timeout": int(os.getenv("ORCHESTRATOR_TIMEOUT", "300"))
        }

    # Configuration is now read-only from .env file
    # No set/save methods needed - edit .env directly

    def validate_config(self) -> bool:
        """Waliduje konfigurację"""
        errors = []

        # Sprawdź OpenAI
        openai_key = self.get_openai_key()
        if openai_key and not openai_key.startswith('sk-'):
            errors.append("OpenAI key should start with 'sk-'")

        # Sprawdź Anthropic
        anthropic_key = self.get_anthropic_key()
        if anthropic_key and not anthropic_key.startswith('sk-ant-'):
            errors.append("Anthropic key should start with 'sk-ant-'")

        if errors:
            print("❌ Configuration issues:")
            for error in errors:
                print(f"   • {error}")
            return False

        return True

    def show_status(self):
        """Pokazuje status konfiguracji"""
        print("📊 AI Orchestrator Configuration Status")
        print("=" * 42)

        openai_configured = bool(self.get_openai_key())
        anthropic_configured = bool(self.get_anthropic_key())

        print(f"🤖 OpenAI: {'✅ Configured' if openai_configured else '❌ Not configured'}")
        print(f"🧠 Anthropic: {'✅ Configured' if anthropic_configured else '❌ Not configured'}")
        print(f"🔐 Encryption: {'✅ Enabled' if self.encrypt else '❌ Disabled'}")

        if openai_configured or anthropic_configured:
            print("\n🎯 Ready to use!")
        else:
            print("\n⚠️  No API keys configured. Run setup first.")


def main():
    """CLI dla prostego configu"""
    import argparse

    parser = argparse.ArgumentParser(description="AI Orchestrator Simple Config")
    parser.add_argument('command', nargs='?', default='status',
                       choices=['setup', 'status', 'validate', 'encrypt', 'decrypt'],
                       help='Command to run')

    args = parser.parse_args()

    # Sprawdź czy jesteśmy w odpowiednim katalogu
    if not Path("ai_simple_config.py").exists():
        print("❌ Run from .cursor directory: cd .cursor && python ai_simple_config.py")
        return

    config = AISimpleConfig()

    if args.command == 'setup':
        config.setup_interactive()
    elif args.command == 'status':
        config.show_status()
    elif args.command == 'validate':
        if config.validate_config():
            print("✅ Configuration is valid")
        else:
            print("❌ Configuration has issues")
    elif args.command == 'encrypt':
        if not CRYPTO_AVAILABLE:
            print("❌ cryptography library required for encryption")
            return
        config.encrypt = True
        config.save_config()
        print("🔐 Configuration encrypted")
    elif args.command == 'decrypt':
        if not CRYPTO_AVAILABLE:
            print("❌ cryptography library required for decryption")
            return
        config.encrypt = False
        config.save_config()
        print("🔓 Configuration decrypted")


if __name__ == "__main__":
    main()
