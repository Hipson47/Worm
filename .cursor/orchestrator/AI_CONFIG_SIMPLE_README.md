# 🔧 Simple Config for AI Orchestrator

This system is **much simpler** than the previous secure config. It uses a plain JSON file with optional encryption.

## 🚀 Quick Start

### 1. Interactive Setup (Recommended)
```bash
cd .cursor/orchestrator
python ai_simple_config.py setup
```

### 2. Manual Editing
Edit `ai_config.json` and enter your API keys:

```json
{
  "openai": {
    "api_key": "sk-your-openai-key-here",
    "model": "gpt-4",
    "max_tokens": 2000
  }
}
```

### 3. Check Status
```bash
python ai_simple_config.py status
```

### 4. Start Orchestrator
```bash
python ai_orchestrator.py
```

## 📁 Configuration Files

- **`ai_config.json`** - Main configuration file (JSON)
- **`ai_config.enc`** - Encrypted version (optional)

## 🔑 Managing API Keys

### Add OpenAI Key
```bash
python ai_simple_config.py setup
# Choose OpenAI and paste your key
```

### Add Anthropic Key
```bash
python ai_simple_config.py setup
# Choose Anthropic and paste your key
```

## 🔐 Encryption (Optional)

### Enable Encryption
```bash
python ai_simple_config.py encrypt
```

### Disable Encryption
```bash
python ai_simple_config.py decrypt
```

> **⚠️ Note**: Encryption uses a simple key. For production, consider a full security setup.

## 🧪 Configuration Testing

### Validate
```bash
python ai_simple_config.py validate
```

### Status
```bash
python ai_simple_config.py status
```

## 📋 Example Configuration

```json
{
  "openai": {
    "api_key": "sk-proj-your-key-here",
    "model": "gpt-4",
    "max_tokens": 2000,
    "temperature": 0.3
  },
  "anthropic": {
    "api_key": "",
    "model": "claude-3-sonnet"
  },
  "orchestrator": {
    "auto_save": true,
    "log_level": "INFO",
    "cache_enabled": true
  }
}
```

## 🔒 Security

- ✅ API keys are not stored in code
- ✅ Optional file encryption
- ✅ Isolated from other `.env` files
- ⚠️  Do not commit `ai_config.json` to git
- ⚠️  Use a full security system in production

## 🆘 Troubleshooting

### "No API keys configured"
Run setup: `python ai_simple_config.py setup`

### "cryptography library required"
Install: `pip install cryptography`

### "Invalid API key format"
Ensure the key starts with `sk-` (OpenAI) or `sk-ant-` (Anthropic)

---

**Pro Tip**: For maximum production security, consider migrating to a full `ai_config_manager.py` solution.
