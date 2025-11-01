# 🤖 AI Orchestrator - Automated MCP Server Setup

Automatycznie skonfigurowany system AI Orchestrator z MCP (Model Context Protocol) dla Cursor.

## 🚀 Szybki Start (3 Kroki)

### 1. Automatyczna Instalacja
```bash
# Uruchom automatyczny setup (Python 3.8+, pip, git)
./setup_orchestrator.sh
```

### 2. Konfiguracja API (jeśli potrzebne)
```bash
# Setup uruchomi się automatycznie, ale jeśli potrzebujesz ręcznej konfiguracji:
python .cursor/orchestrator/setup_ai_config.py
```

### 3. Uruchomienie
```bash
# Automatyczne uruchomienie z virtual environment
./run_orchestrator.sh

# Lub ręczne:
source orchestrator_venv/bin/activate  # Linux/Mac
# orchestrator_venv\Scripts\activate   # Windows
bash .cursor/orchestrator/start_mcp_server.sh
```

## 📋 Co Robi Automatyczny Setup

### ✅ Sprawdzanie Wymagań
- Python 3.8+
- pip
- git (dla aktualizacji)

### ✅ Tworzenie Środowiska
- Virtual Environment (`orchestrator_venv/`)
- Izolacja zależności
- Łatwe zarządzanie wersjami

### ✅ Instalacja Zależności
- Wszystkie wymagane biblioteki Python
- ChromaDB dla RAG
- OpenAI/Anthropic API clients
- MCP framework

### ✅ Konfiguracja API
- Interaktywny setup kluczy API
- Bezpieczne przechowywanie w `.env`
- Walidacja kluczy

### ✅ Testowanie
- Weryfikacja MCP server
- Testowanie funkcjonalności
- Raportowanie błędów

### ✅ Skróty Uruchamiania
- `run_orchestrator.sh` - łatwe uruchomienie
- Automatyczna aktywacja virtual environment

## 🛠️ Opcje Setup

### Pełny Setup (Domyślny)
```bash
./setup_orchestrator.sh
```

### Clean Setup (Usuwa istniejące środowisko)
```bash
./setup_orchestrator.sh --clean
```

### Tylko Test (sprawdza istniejące środowisko)
```bash
./setup_orchestrator.sh --test-only
```

### Pomoc
```bash
./setup_orchestrator.sh --help
```

## 📁 Struktura Projektu

```
AiBook/
├── .env                          # Konfiguracja API (bezpieczna)
├── .cursor/
│   ├── orchestrator/
│   │   ├── mcp_server.py        # MCP server z stdio transport
│   │   ├── rag_engine.py         # RAG dla wiedzy
│   │   ├── ai_orchestrator.py    # Główna logika AI
│   │   ├── requirements.txt      # Zależności Python
│   │   └── start_mcp_server.sh  # Uruchamianie MCP
│   └── knowledge/                # Baza wiedzy RAG
├── orchestrator_venv/            # Virtual environment (auto-created)
├── setup_orchestrator.sh         # Automatyczny setup
├── run_orchestrator.sh           # Łatwe uruchomienie
└── ORCHESTRATOR_README.md         # Ten plik
```

## 🔧 Jak To Działa

### Architektura MCP
```
Cursor → MCP Tools → Orchestrator → AI Models + Knowledge Base
       stdio transport    RAG-enabled   OpenAI/Claude APIs
```

### Automatyzacja
1. **Setup Script**: Jednorazowa konfiguracja całego środowiska
2. **Virtual Environment**: Izolacja i spójność
3. **Auto-aktywacja**: Automatyczne uruchamianie z venv
4. **RAG Updates**: Automatyczne aktualizowanie bazy wiedzy
5. **Error Recovery**: Fallback przy błędach

## 🚨 Troubleshooting

### Problem: "Python nie znaleziony"
```bash
# Zainstaluj Python 3.8+
sudo apt install python3.8 python3-pip  # Ubuntu/Debian
brew install python3                    # macOS
# Windows: pobierz z python.org
```

### Problem: "Virtual environment nie istnieje"
```bash
# Uruchom setup ponownie
./setup_orchestrator.sh --clean
```

### Problem: "API key nie skonfigurowany"
```bash
# Uruchom konfigurację API
python .cursor/orchestrator/setup_ai_config.py
```

### Problem: "MCP server nie uruchamia się"
```bash
# Sprawdź logi
./setup_orchestrator.sh --test-only

# Ręczne uruchomienie dla debugowania
source orchestrator_venv/bin/activate
python -c "from orchestrator.mcp_server import MCPStdIOServer; print('Import OK')"
```

## 🔒 Bezpieczeństwo

### API Keys
- Przechowywane w `.env` (ignorowane przez git)
- Szyfrowane podczas konfiguracji
- Nigdy nie logowane

### Virtual Environment
- Izolacja zależności
- Brak konfliktów systemowych
- Łatwe usuwanie/resetowanie

### MCP Transport
- Stdio (bez otwartych portów)
- Brak sieciowej ekspozycji
- Bezpieczna komunikacja z Cursor

## 📊 Monitorowanie

### Logi Systemowe
```bash
# Logi MCP server
tail -f /tmp/mcp_server.log

# Logi AI Orchestrator
tail -f .cursor/orchestrator/ai_orchestrator.log
```

### Metryki Wydajności
- Czas odpowiedzi MCP
- Zużycie pamięci RAG
- Trafność rekomendacji AI
- Czas aktualizacji wiedzy

## 🔄 Aktualizacje

### Automatyczne
- Baza wiedzy aktualizuje się co 30 sekund
- Sprawdzenie nowych plików w `.cursor/knowledge/`

### Manualne
```bash
# Aktualizacja kodu
git pull

# Aktualizacja zależności
source orchestrator_venv/bin/activate
pip install -r .cursor/orchestrator/requirements.txt --upgrade
```

## 🤝 Wsparcie

### Problemy?
1. Sprawdź logi: `./setup_orchestrator.sh --test-only`
2. Zrestartuj: `./setup_orchestrator.sh --clean`
3. Sprawdź dokumentację MCP: https://modelcontextprotocol.io/

### Rozszerzenia
- Dodaj nowe MCP tools w `mcp_server.py`
- Rozszerz bazę wiedzy w `.cursor/knowledge/`
- Dodaj nowe AI capabilities w `ai_orchestrator.py`

---

## 🎯 Status: W PEŁNI AUTOMATYZOWANY

✅ **Jednorazowy setup** → ✅ **Automatyczne uruchomienie** → ✅ **Ciągła praca**

System jest teraz **w pełni automatyczny** - od instalacji po codzienną pracę! 🚀🤖✨
