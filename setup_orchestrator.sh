#!/bin/bash
# AI Orchestrator Automated Setup Script
# Automatycznie konfiguruje virtual environment i uruchamia MCP server

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
VENV_NAME="orchestrator_venv"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ORCHESTRATOR_DIR="$SCRIPT_DIR/.cursor/orchestrator"
REQUIREMENTS_FILE="$ORCHESTRATOR_DIR/requirements.txt"
ENV_FILE="$SCRIPT_DIR/.env"

# Logging functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check Python version
check_python() {
    log_info "Checking Python version..."

    if ! command_exists python3 && ! command_exists python; then
        log_error "Python is not installed. Please install Python 3.8+ first."
        exit 1
    fi

    # Use python3 if available, otherwise python
    if command_exists python3; then
        PYTHON_CMD="python3"
    else
        PYTHON_CMD="python"
    fi

    # Check version
    PYTHON_VERSION=$($PYTHON_CMD --version 2>&1 | grep -oP '\d+\.\d+')
    PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d. -f1)
    PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d. -f2)

    if [ "$PYTHON_MAJOR" -lt 3 ] || ([ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -lt 8 ]); then
        log_error "Python 3.8+ is required. Current version: $PYTHON_VERSION"
        exit 1
    fi

    log_success "Python $PYTHON_VERSION found ✓"
}

# Create virtual environment
create_venv() {
    log_info "Setting up virtual environment..."

    if [ -d "$VENV_NAME" ]; then
        log_warning "Virtual environment already exists at $VENV_NAME"
        log_info "Using existing virtual environment"
        return 0
    fi

    log_info "Creating virtual environment: $VENV_NAME"
    $PYTHON_CMD -m venv "$VENV_NAME"

    if [ ! -d "$VENV_NAME" ]; then
        log_error "Failed to create virtual environment"
        exit 1
    fi

    log_success "Virtual environment created ✓"
}

# Activate virtual environment and install dependencies
setup_dependencies() {
    log_info "Installing dependencies..."

    # Activate virtual environment
    if [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "win32" ]]; then
        # Windows
        source "$VENV_NAME/Scripts/activate"
    else
        # Unix-like systems
        source "$VENV_NAME/bin/activate"
    fi

    # Upgrade pip
    pip install --upgrade pip

    # Install requirements
    if [ -f "$REQUIREMENTS_FILE" ]; then
        pip install -r "$REQUIREMENTS_FILE"
        log_success "Dependencies installed ✓"
    else
        log_error "Requirements file not found: $REQUIREMENTS_FILE"
        exit 1
    fi

    # Deactivate venv (will be activated again when running)
    deactivate
}

# Setup .env file if not exists
setup_env() {
    log_info "Checking .env configuration..."

    if [ -f "$ENV_FILE" ]; then
        log_success ".env file exists ✓"
        return 0
    fi

    log_warning ".env file not found"

    # Try to run setup script
    if [ -f "$ORCHESTRATOR_DIR/setup_ai_config.py" ]; then
        log_info "Running AI configuration setup..."

        # Activate venv temporarily
        if [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "win32" ]]; then
            source "$VENV_NAME/Scripts/activate"
        else
            source "$VENV_NAME/bin/activate"
        fi

        $PYTHON_CMD "$ORCHESTRATOR_DIR/setup_ai_config.py"

        deactivate

        if [ -f "$ENV_FILE" ]; then
            log_success ".env file created ✓"
        else
            log_error "Failed to create .env file"
            exit 1
        fi
    else
        log_error "Setup script not found: $ORCHESTRATOR_DIR/setup_ai_config.py"
        exit 1
    fi
}

# Test MCP server
test_server() {
    log_info "Testing MCP server..."

    # Activate venv
    if [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "win32" ]]; then
        source "$VENV_NAME/Scripts/activate"
    else
        source "$VENV_NAME/bin/activate"
    fi

    # Test server startup (timeout after 10 seconds)
    timeout 10s bash "$ORCHESTRATOR_DIR/start_mcp_server.sh" << 'EOF' >/dev/null 2>&1
{"jsonrpc": "2.0", "id": "test", "method": "ping", "params": {}}
EOF

    if [ $? -eq 0 ]; then
        log_success "MCP server test passed ✓"
    else
        log_error "MCP server test failed"
        exit 1
    fi

    deactivate
}

# Create desktop shortcut/menu entry (optional)
create_shortcut() {
    log_info "Creating launcher script..."

    cat > run_orchestrator.sh << EOF
#!/bin/bash
# AI Orchestrator Launcher
# Automatically activates virtual environment and runs MCP server

SCRIPT_DIR="\$(cd "\$(dirname "\${BASH_SOURCE[0]}")" && pwd)"

# Activate virtual environment
if [[ "\$OSTYPE" == "msys" ]] || [[ "\$OSTYPE" == "win32" ]]; then
    source "\$SCRIPT_DIR/$VENV_NAME/Scripts/activate"
else
    source "\$SCRIPT_DIR/$VENV_NAME/bin/activate"
fi

# Run MCP server
bash "\$SCRIPT_DIR/.cursor/orchestrator/start_mcp_server.sh"

# Deactivate when done
deactivate
EOF

    chmod +x run_orchestrator.sh
    log_success "Launcher script created: run_orchestrator.sh"
}

# Main setup function
main() {
    echo "🤖 AI Orchestrator Automated Setup"
    echo "=================================="

    check_python
    create_venv
    setup_dependencies
    setup_env
    test_server
    create_shortcut

    echo
    log_success "🎉 AI Orchestrator setup completed successfully!"
    echo
    echo "To run the orchestrator:"
    echo "  ./run_orchestrator.sh"
    echo
    echo "Or manually:"
    echo "  source $VENV_NAME/bin/activate"
    echo "  bash .cursor/orchestrator/start_mcp_server.sh"
}

# Handle command line arguments
case "${1:-}" in
    "--help"|"-h")
        echo "AI Orchestrator Setup Script"
        echo ""
        echo "Usage: $0 [OPTIONS]"
        echo ""
        echo "Options:"
        echo "  --help, -h          Show this help message"
        echo "  --clean              Remove virtual environment and start fresh"
        echo "  --test-only          Only run tests (skip setup)"
        echo ""
        echo "Examples:"
        echo "  $0                   # Full setup"
        echo "  $0 --clean          # Clean setup"
        echo "  $0 --test-only      # Test existing setup"
        ;;
    "--clean")
        log_info "Cleaning up existing setup..."
        rm -rf "$VENV_NAME"
        rm -f run_orchestrator.sh
        log_success "Cleanup completed"
        main
        ;;
    "--test-only")
        log_info "Testing existing setup..."
        if [ ! -d "$VENV_NAME" ]; then
            log_error "Virtual environment not found. Run setup first."
            exit 1
        fi
        test_server
        log_success "Test completed"
        ;;
    *)
        main
        ;;
esac
