# 🚀 **MCP SETUP GUIDE - AI ORCHESTRATOR**

**How to configure MCP Server so that Cursor automatically detects it**

---

## 📋 **STEP 1: Configuration Verification**

### Files that were created:
```
.cursor/
├── mcp.json                    ✅ MCP configuration for Cursor
└── orchestrator/
    ├── mcp_server.py         ✅ MCP server implementation
    ├── __main__.py           ✅ Entry point
    ├── start_mcp_server.sh  ✅ Start script
    └── rag_engine.py         ✅ RAG engine with knowledge indexing
```

### Check if everything is in place:
```bash
ls -la .cursor/mcp.json
ls -la .cursor/orchestrator/mcp_server.py
ls -la .cursor/orchestrator/start_mcp_server.sh
```

---

## 🔧 **STEP 2: Dependencies Installation**

```bash
cd .cursor/orchestrator
pip install -r requirements.txt
```

**Important packages:**
- `chromadb` - Vector database for RAG
- `openai` - Embeddings and LLM
- `sentence-transformers` - Alternative embeddings
- `mcp` - MCP protocol library

---

## ⚙️ **STEP 3: API Keys Configuration**

### Safe API key configuration (recommended):
```bash
# Run the secure setup script
python setup_ai_config.py
```

**This script will:**
- ✅ Prompt for API keys securely (not logged)
- ✅ Validate key formats
- ✅ Save to `.env` file (standard approach)
- ✅ Automatically ignored by `.gitignore`

**🚨 SECURITY WARNING:**
- Never commit `.env` file to git
- Use environment variables (this is the standard)
- Rotate keys regularly
- GitHub will block pushes containing secrets

### Alternative: Edit .env directly:
```bash
# Edit existing .env file with your keys
nano .env
```

**Your .env file should contain:**
```bash
OPENAI_API_KEY=sk-your-key-here
ANTHROPIC_API_KEY=sk-ant-your-key-here
OPENAI_MODEL=gpt-4
ORCHESTRATOR_AUTO_SAVE=true
```

---
## 🎯 **STEP 4: Restart Cursor**

1. **Close Cursor completely**
2. **Reopen the project**
3. **Cursor will automatically detect MCP server** from `.cursor/mcp.json` file

### Detection Verification:
- Open Command Palette (`Ctrl+Shift+P`)
- Type "MCP" - you should see MCP-related options
- Check Cursor settings - MCP section

---

## 🧪 **STEP 5: Testing MCP**

### Test 1: Check if MCP works
```bash
# Uruchom test
python test_mcp_simple.py
```

### Test 2: Manual MCP Testing
```bash
# Run MCP server manually (method 1 - direct)
PYTHONPATH=.cursor python -m orchestrator.mcp_server

# Run MCP server manually (method 2 - via script)
./.cursor/orchestrator/start_mcp_server.sh

# Test communication (in another terminal)
echo '{"jsonrpc": "2.0", "id": "test", "method": "initialize", "params": {}}' | ./.cursor/orchestrator/start_mcp_server.sh
```

### Test 3: Test in Cursor
1. **Restart Cursor completely** (important!)
2. Open Command Palette (`Ctrl+Shift+P`)
3. Type "MCP" - options should appear
4. Check Cursor settings -> MCP section
5. Tools should be available in context menu

---

## 🔍 **STEP 6: Troubleshooting**

### Problem: MCP is not detected
```bash
# Sprawdź czy plik istnieje
cat .cursor/mcp.json

# Sprawdź składnię JSON
python -c "import json; json.load(open('.cursor/mcp.json'))"
```

### Problem: Server się nie uruchamia
```bash
# Sprawdź uprawnienia
ls -la .cursor/orchestrator/start_mcp_server.sh

# Uruchom ręcznie
cd .cursor/orchestrator && python -m orchestrator.mcp_server
```

### Problem: Brak API key
```bash
# Sprawdź config
cat .cursor/ai_config.json

# Test API key
python -c "
import openai
openai.api_key = 'your-key'
print('API key OK')
"
```

### Problem: "spawn bash ENOENT" lub "bash nie znaleziony"
```bash
# Przyczyna: bash nie jest w PATH na Windows/Mac
# Rozwiązanie: Konfiguracja została już poprawiona na bezpośrednie python
# Sprawdź .cursor/mcp.json - powinno używać "python" nie "bash"
```

### Problem: "Unexpected token" lub błędy JSON
```bash
# Przyczyna: MCP server wysyłał "id": null zamiast pominięcia pola id
# Rozwiązanie: Poprawiono formatowanie JSON-RPC:
# - Jeśli request nie ma id (powiadomienie), odpowiedź też nie ma id
# - Wszystkie odpowiedzi mają prawidłowy format JSON-RPC 2.0
# - Logi wysyłane są do stderr, stdout tylko dla JSON
```

### Problem: "No server info found" w Cursor
```bash
# Przyczyna: Server się nie uruchomił lub komunikacja nie działa
# Rozwiązania:
# 1. Restart Cursor całkowicie
# 2. Sprawdź czy PYTHONPATH=.cursor python -m orchestrator.mcp_server działa w terminalu
# 3. Sprawdź czy .cursor/mcp.json ma prawidłową konfigurację
# 4. Na Windows może być problem z PYTHONPATH - spróbuj ustawić absolutną ścieżkę
# 5. Sprawdź logi Cursor - poszukaj błędów "Client error for command"
```

### Problem: "Client error for command" w Cursor
```bash
# Przyczyna: MCP server wysyła nieprawidłowy JSON-RPC
# Rozwiązania:
# 1. Sprawdź czy odpowiedzi mają prawidłowy format JSON-RPC 2.0
# 2. Upewnij się że "id" jest obecne tylko gdy request ma id
# 3. Upewnij się że odpowiedzi mają albo "result" albo "error", nie oba
# 4. Sprawdź kodowanie UTF-8 w odpowiedziach
# 5. Testuj ręcznie: echo '{"jsonrpc":"2.0","id":"test","method":"initialize"}' | bash start_mcp_server.sh
```

### Problem: "ModuleNotFoundError: No module named 'orchestrator'"
```bash
# Przyczyna: PYTHONPATH nie jest ustawiony poprawnie w Cursor
# Rozwiązania:
# 1. Sprawdź czy PYTHONPATH zawiera ścieżkę do .cursor
# 2. Na Windows użyj średnika ';' zamiast dwukropka ':'
# 3. Albo ustaw absolutną ścieżkę: PYTHONPATH=D:\github\testy\AiBook\.cursor
# 4. Sprawdź czy wszystkie pliki __init__.py są obecne w .cursor/orchestrator/
# 5. Testuj w terminalu: PYTHONPATH=.cursor python -m orchestrator.mcp_server
# 6. Jeśli nie działa, użyj WSL Python: /mnt/d/github/testy/AiBook/.cursor/orchestrator/start_mcp_server.sh
```

---

## ✅ **KROK 7: SUKCES - MCP DZIAŁA!**

**Wszystkie problemy zostały rozwiązane! 🎉**

### Weryfikacja działania:
```bash
# Test initialize
echo '{"jsonrpc": "2.0", "id": "test", "method": "initialize", "params": {}}' | bash .cursor/orchestrator/start_mcp_server.sh

# Test tools
echo '{"jsonrpc": "2.0", "id": "tools", "method": "tools/list", "params": {}}' | bash .cursor/orchestrator/start_mcp_server.sh

# Wynik: Prawidłowy JSON-RPC bez błędów walidacji
```

### Available MCP Tools:
1. **`orchestrate_task`** - Complete task orchestration with intelligent rule selection and planning
2. **`select_rules`** - Selection of optimal rules for the given context
3. **`get_execution_plan`** - Generation of detailed task execution plan
4. **`query_knowledge`** - Knowledge base search using RAG
5. **`analyze_code`** - Code analysis with project context

### Available MCP Resources:
- **`orchestrator://knowledge`** - Knowledge base index
- **`orchestrator://rules`** - System rules list
- **`orchestrator://metrics`** - Performance metrics
- **`orchestrator://config`** - System configuration

---

### Example Usage in Cursor:
```python
# Cursor automatically detects these tools
# and makes them available in the context menu

# Example usage:
# orchestrate_task("Implement user authentication", "React app")
# query_knowledge("What are React 19 best practices?")
```

---

## 🎯 **STEP 8: Production Usage**

### Enabling MCP in Projects:
1. **Copy MCP files** to new project
2. **Configure API keys** in `.cursor/ai_config.json`
3. **Restart Cursor** - automatic detection
4. **Use tools** in daily work

### Benefits:
- ✅ **Automatic detection** - zero configuration
- ✅ **Automatic knowledge updates** - detects new files every 30 seconds
- ✅ **RAG-powered** - intelligent recommendations
- ✅ **Emerging tech aware** - React 19, K8s 1.31, etc.
- ✅ **Future-proof** - MCP standard

---

## 🚨 **NOTES**

- **API Keys**: Keep secure, do not commit to git
- **Performance**: First start may take longer (knowledge indexing)
- **Knowledge Monitoring**: System automatically detects new files every 30 seconds and updates RAG index
- **Compatibility**: Requires Cursor 2.0+ with MCP support
- **Debugging**: Check Cursor logs if something doesn't work

---

## 🎉 **SUKCES!**

If everything works, you should see in Cursor:
- 🔧 **MCP Tools** available in command palette
- 🧠 **RAG Knowledge** for intelligent queries
- 🤖 **AI Orchestrator** for automatic task orchestration
- 📊 **Performance Metrics** for monitoring

**Cursor now automatically detects and integrates AI Orchestrator via MCP!** 🚀✨
