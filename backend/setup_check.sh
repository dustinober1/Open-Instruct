#!/bin/bash

################################################################################
# Open-Instruct Backend Setup Verification Script
# This script checks your setup and provides guidance for any issues found
################################################################################

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Counters
PASSED=0
FAILED=0
WARNINGS=0

################################################################################
# Helper Functions
################################################################################

print_header() {
    echo -e "\n${BLUE}========================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}========================================${NC}\n"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
    ((PASSED++))
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
    ((FAILED++))
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
    ((WARNINGS++))
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

################################################################################
# Check Functions
################################################################################

check_python() {
    print_header "Checking Python Installation"

    if command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
        PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d. -f1)
        PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d. -f2)

        print_success "Python installed: $PYTHON_VERSION"

        if [ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -ge 9 ]; then
            print_success "Python version is compatible (3.9+)"
        else
            print_error "Python version must be 3.9 or higher (current: $PYTHON_VERSION)"
            print_info "Install Python 3.9+ from https://www.python.org/downloads/"
        fi
    else
        print_error "Python 3 not found"
        print_info "Install Python 3.9+ from https://www.python.org/downloads/"
    fi
}

check_virtualenv() {
    print_header "Checking Virtual Environment"

    if [ -z "$VIRTUAL_ENV" ]; then
        print_error "Virtual environment is not activated"

        if [ -d "venv" ]; then
            print_info "Virtual environment exists but is not activated"
            print_info "Run: source venv/bin/activate"
        else
            print_warning "Virtual environment not found"
            print_info "Create it with: python3 -m venv venv"
            print_info "Then activate it with: source venv/bin/activate"
        fi
    else
        print_success "Virtual environment activated: $VIRTUAL_ENV"
    fi
}

check_dependencies() {
    print_header "Checking Python Dependencies"

    if [ -z "$VIRTUAL_ENV" ]; then
        print_error "Cannot check dependencies - virtual environment not activated"
        return
    fi

    local required_packages=(
        "fastapi"
        "dspy-ai"
        "pydantic"
        "uvicorn"
        "pytest"
    )

    local missing_packages=()

    for package in "${required_packages[@]}"; do
        if python3 -c "import ${package//-/_}" 2>/dev/null; then
            print_success "$package is installed"
        else
            print_error "$package is NOT installed"
            missing_packages+=("$package")
        fi
    done

    if [ ${#missing_packages[@]} -gt 0 ]; then
        print_warning "Missing packages: ${missing_packages[*]}"
        print_info "Install with: pip install -r requirements.txt"
    fi
}

check_ollama() {
    print_header "Checking Ollama Installation"

    if command -v ollama &> /dev/null; then
        print_success "Ollama is installed"

        # Check if Ollama is running
        if curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
            print_success "Ollama is running"

            # Check available models
            MODELS=$(ollama list 2>/dev/null | grep -v "NAME" || true)
            if [ -n "$MODELS" ]; then
                print_success "Ollama models installed:"
                echo "$MODELS" | while read -r line; do
                    echo "  - $line"
                done

                # Check for recommended model
                if echo "$MODELS" | grep -q "deepseek-r1:1.5b"; then
                    print_success "Recommended model (deepseek-r1:1.5b) is installed"
                else
                    print_warning "Recommended model (deepseek-r1:1.5b) not found"
                    print_info "Install it with: ollama pull deepseek-r1:1.5b"
                fi
            else
                print_warning "No Ollama models installed"
                print_info "Install a model with: ollama pull deepseek-r1:1.5b"
            fi
        else
            print_error "Ollama is not running"
            print_info "Start Ollama with:"
            print_info "  macOS: brew services start ollama"
            print_info "  Linux: sudo systemctl start ollama"
            print_info "  Or run: ollama serve"
        fi
    else
        print_warning "Ollama not found"
        print_info "Install Ollama from https://ollama.ai/download"
        print_info "Or with Homebrew (macOS): brew install ollama"
    fi
}

check_env_file() {
    print_header "Checking Environment Configuration"

    if [ -f ".env" ]; then
        print_success ".env file exists"

        # Check for required variables
        if grep -q "OLLAMA_BASE_URL" .env; then
            print_success "OLLAMA_BASE_URL is configured"
        else
            print_warning "OLLAMA_BASE_URL not found in .env"
        fi

        if grep -q "OLLAMA_MODEL" .env; then
            print_success "OLLAMA_MODEL is configured"
        else
            print_warning "OLLAMA_MODEL not found in .env"
        fi

        if grep -q "DATABASE_URL" .env; then
            print_success "DATABASE_URL is configured"
        else
            print_warning "DATABASE_URL not found in .env"
        fi
    else
        print_warning ".env file not found"
        print_info "Create .env file with:"
        print_info "  cat > .env << EOF"
        print_info "  OLLAMA_BASE_URL=http://localhost:11434"
        print_info "  OLLAMA_MODEL=deepseek-r1:1.5b"
        print_info "  DATABASE_URL=sqlite:///./data/open_instruct.db"
        print_info "  LOG_LEVEL=INFO"
        print_info "  EOF"
    fi
}

check_directories() {
    print_header "Checking Project Structure"

    local required_dirs=(
        "src"
        "src/api"
        "src/core"
        "src/modules"
        "tests"
        "data"
        "logs"
    )

    for dir in "${required_dirs[@]}"; do
        if [ -d "$dir" ]; then
            print_success "Directory exists: $dir/"
        else
            print_error "Directory missing: $dir/"
            if [ "$dir" == "data" ] || [ "$dir" == "logs" ]; then
                print_info "Create with: mkdir -p $dir"
            fi
        fi
    done
}

check_api_server() {
    print_header "Testing API Server"

    if [ -z "$VIRTUAL_ENV" ]; then
        print_warning "Cannot test API - virtual environment not activated"
        return
    fi

    # Check if server is running
    if curl -s http://localhost:8000/health > /dev/null 2>&1; then
        print_success "API server is running on port 8000"

        # Test health endpoint
        HEALTH_RESPONSE=$(curl -s http://localhost:8000/health)
        if echo "$HEALTH_RESPONSE" | grep -q "healthy"; then
            print_success "Health check passed"
        else
            print_warning "Health check shows degraded state"
        fi
    else
        print_warning "API server is not running"
        print_info "Start it with: uvicorn src.api.main:app --reload"
    fi
}

################################################################################
# Main Execution
################################################################################

main() {
    echo -e "${BLUE}"
    echo "╔════════════════════════════════════════════════════════════╗"
    echo "║   Open-Instruct Backend Setup Verification                ║"
    echo "║   Version 1.0.0                                           ║"
    echo "╚════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"

    # Change to backend directory if script is run from elsewhere
    if [ -f "setup_check.sh" ]; then
        cd "$(dirname "$0")" || exit 1
    fi

    print_info "Running checks from: $(pwd)"

    # Run all checks
    check_python
    check_virtualenv
    check_dependencies
    check_ollama
    check_env_file
    check_directories
    check_api_server

    # Print summary
    print_header "Check Summary"
    echo -e "${GREEN}Passed: $PASSED${NC}"
    echo -e "${YELLOW}Warnings: $WARNINGS${NC}"
    echo -e "${RED}Failed: $FAILED${NC}"

    if [ $FAILED -eq 0 ] && [ $WARNINGS -eq 0 ]; then
        echo -e "\n${GREEN}🎉 All checks passed! Your setup is ready.${NC}\n"
        print_info "Start the API server with:"
        print_info "  uvicorn src.api.main:app --reload"
        print_info "Then visit http://localhost:8000/docs for API documentation"
        exit 0
    elif [ $FAILED -eq 0 ]; then
        echo -e "\n${YELLOW}⚠️  Setup is mostly ready, but there are some warnings.${NC}\n"
        print_info "Review the warnings above and follow the suggested fixes."
        exit 0
    else
        echo -e "\n${RED}❌ Setup has issues that need to be fixed.${NC}\n"
        print_info "Please follow the suggested fixes above."
        exit 1
    fi
}

# Run main function
main
