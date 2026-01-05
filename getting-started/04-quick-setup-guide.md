# 🛠️ Quick Setup Guide: Step-by-Step Installation

**Version**: 1.0.0
**Last Updated**: 2025-01-05

---

## 🎯 Mission: Complete Setup in 15 Minutes

This guide walks you through setting up your development environment for the Open-Instruct project. Follow these steps carefully.

---

## 📋 Prerequisites

Before starting, ensure you have:
- ✅ **Python 3.9+** installed
- ✅ **Git** installed and configured
- ✅ **15-20 minutes** of uninterrupted time
- ✅ **Stable internet connection**

---

## 🚀 Step 1: Clone the Repository (2 minutes)

### If You Haven't Cloned Yet
```bash
# Clone the repository
git clone <repository-url>
cd Open_Instruct

# Verify the structure
ls -la
```

### Expected Output
```
README.md
getting-started/
documentation/
examples/
resources/
```

---

## 🚀 Step 2: Set Up Project Structure (3 minutes)

### Create Backend Directory
```bash
# Create the backend directory structure
mkdir -p backend/src/{core,modules} tests logs data

# Verify the structure
tree backend/  # Or use: find backend/ -type d
```

### Expected Structure
```
backend/
├── src/
│   ├── core/      # Core business logic
│   └── modules/   # DSPy modules
├── tests/         # Test files
├── logs/          # Log files
└── data/          # Database and cache
```

---

## 🚀 Step 3: Set Up Virtual Environment (3 minutes)

### Navigate to Backend
```bash
cd backend
```

### Create and Activate Virtual Environment

#### macOS/Linux
```bash
# Create virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate

# Verify activation
echo $VIRTUAL_ENV  # Should show path to venv
```

#### Windows
```cmd
# Create virtual environment
python -m venv venv

# Activate it
venv\Scripts\activate

# Verify activation
echo %VIRTUAL_ENV%
```

### Verify Virtual Environment
```bash
# Should show (venv) at the beginning of your prompt
which python  # Should show venv/bin/python
which pip     # Should show venv/bin/pip
```

---

## 🚀 Step 4: Install Dependencies (4 minutes)

### Upgrade Pip First
```bash
# Upgrade pip to latest version
pip install --upgrade pip
```

### Install Core Dependencies
```bash
# Install main dependencies
pip install dspy-ai pydantic fastapi uvicorn pytest

# Install development dependencies
pip install pytest-cov black flake8 pre-commit
```

### Verify Installation
```bash
# Test imports
python -c "
import dspy
import pydantic
import fastapi
import uvicorn
import pytest
print('✅ All core packages installed successfully!')
print(f'DSPy version: {dspy.__version__}')
"
```

### Expected Output
```
✅ All core packages installed successfully!
DSPy version: 2.X.X
```

---

## 🚀 Step 5: Set Up Ollama (3 minutes)

### Check if Ollama is Running
```bash
# Check if Ollama is installed and running
ollama list
```

#### If Ollama is Not Installed

**Option 1: Homebrew (macOS)**
```bash
brew install ollama
```

**Option 2: Direct Download**
1. Visit: https://ollama.ai/download
2. Download for your operating system
3. Follow the installation instructions

**Option 3: Docker**
```bash
# Pull and run Ollama Docker container
docker run -d -p 11434:11434 --name ollama ollama/ollama
```

### Install DeepSeek-R1 Model
```bash
# Pull the required model
ollama pull deepseek-r1:1.5b

# Wait for download to complete (this may take a few minutes)
```

### Verify Model Installation
```bash
# List installed models
ollama list
```

#### Expected Output
```
NAME            ID              SIZE    MODIFIED
deepseek-r1:1.5b        abc123  2.1 GB    2 hours ago
```

---

## 🚀 Step 6: Create Initial Configuration (2 minutes)

### Create Environment File
```bash
# Create .env file
cat > .env << 'EOF'
# Open-Instruct Environment Configuration

# Database
DATABASE_URL=sqlite:///data/open_instruct.db

# Ollama Configuration
OLLAMA_HOST=http://localhost:11434
OLLAMA_MODEL=deepseek-r1:1.5b

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
API_RELOAD=True

# Logging
LOG_LEVEL=INFO
LOG_FILE=logs/production.log

# Caching
CACHE_TTL=3600  # 1 hour
CACHE_SIZE=1000

# LLM Configuration
LLM_TEMPERATURE=0.1
LLM_MAX_TOKENS=1000
LLM_TOP_P=0.9
EOF
```

### Create .gitignore
```bash
# Create .gitignore file
cat > .gitignore << 'EOF'
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Virtual Environment
venv/
ENV/

# IDE
.vscode/
.idea/
*.swp
*.swo

# Database
*.db
*.sqlite
*.sqlite3

# Logs
*.log
logs/

# Environment
.env
.env.local
.env.*.local

# Ollama models (optional, large files)
models/

# Testing
.pytest_cache/
.coverage
htmlcov/
.tox/

# OS
.DS_Store
Thumbs.db

# Data files (can contain sensitive info)
data/
cache/
```

---

## 🚀 Step 7: Create First Test (2 minutes)

### Create Test Directory
```bash
# Create test directory
mkdir -p tests/unit
```

### Create Initial Test File
```bash
# Create initial test
cat > tests/test_hello.py << 'EOF'
"""Initial test file to verify setup"""

def test_hello_world():
    """Test that basic Python works"""
    assert 1 + 1 == 2

def test_environment():
    """Test that environment is set up correctly"""
    import os
    assert os.environ.get('VIRTUAL_ENV') is not None

def test_imports():
    """Test that all packages can be imported"""
    import dspy
    import pydantic
    import fastapi
    import uvicorn
    import pytest
    print("✅ All imports successful!")

def test_ollama_connection():
    """Test that Ollama is accessible"""
    import subprocess
    result = subprocess.run(['ollama', 'list'], capture_output=True, text=True)
    assert result.returncode == 0
    print("✅ Ollama is accessible")
EOF
```

### Run the Test
```bash
# Run all tests
pytest tests/test_hello.py -v

# Or run with coverage
pytest tests/test_hello.py --cov=.
```

### Expected Output
```
============================= test session starts ==============================
collected 4 items

tests/test_hello.py::test_hello_world PASSED                         [ 25%]
tests/test_hello.py::test_environment PASSED                           [ 50%]
tests/test_hello.py::test_imports PASSED                              [ 75%]
tests/test_hello.py::test_ollama_connection PASSED                    [100%]

============================== 4 passed in 0.12s ===============================
```

---

## 🚀 Step 8: Verify Setup (1 minute)

### Run Final Verification
```bash
# Create a verification script
cat > verify_setup.py << 'EOF'
#!/usr/bin/env python3
"""Verify all setup components are working"""

def check_python():
    import sys
    print(f"✅ Python: {sys.version}")

def check_packages():
    packages = ['dspy', 'pydantic', 'fastapi', 'uvicorn', 'pytest']
    for pkg in packages:
        try:
            __import__(pkg)
            print(f"✅ {pkg}: installed")
        except ImportError:
            print(f"❌ {pkg}: missing")

def check_ollama():
    import subprocess
    result = subprocess.run(['ollama', 'list'], capture_output=True, text=True)
    if result.returncode == 0:
        print("✅ Ollama: running")
    else:
        print("❌ Ollama: not running")

def check_directories():
    import os
    dirs = ['tests', 'logs', 'data', 'src/core', 'src/modules']
    for dir in dirs:
        if os.path.exists(dir):
            print(f"✅ {dir}: exists")
        else:
            print(f"❌ {dir}: missing")

if __name__ == "__main__":
    print("🔍 Verifying Open-Instruct Setup")
    print("=" * 40)
    check_python()
    check_packages()
    check_ollama()
    check_directories()
    print("=" * 40)
    print("✅ Setup verification complete!")
EOF

# Run verification
python verify_setup.py
```

### Expected Output
```
🔍 Verifying Open-Instruct Setup
========================================
✅ Python: 3.9.7 (default, ...)
✅ dspy: installed
✅ pydantic: installed
✅ fastapi: installed
✅ uvicorn: installed
✅ pytest: installed
✅ Ollama: running
✅ tests: exists
✅ logs: exists
✅ data: exists
✅ src/core: exists
✅ src/modules: exists
========================================
✅ Setup verification complete!
```

---

## 🎉 Setup Complete!

### ✅ You've Successfully:
- [ ] Cloned the repository
- [ ] Created project structure
- [ ] Set up virtual environment
- [ ] Installed dependencies
- [ ] Set up Ollama
- [ ] Created configuration files
- [ ] Verified setup with tests

### 🚀 Next Steps

#### Option 1: Follow Implementation Plan
```bash
# Read the implementation plan
cat documentation/implementation-plan.md

# Start Week 1, Day 1
```

#### Option 2: Try a Quick Example
```bash
# Try a simple DSPy example
python -c "
import dspy
print('✅ DSPy is working!')
print(f'Version: {dspy.__version__}')
"
```

#### Option 3: Start the API Server
```bash
# Start the FastAPI development server
uvicorn src.api:app --reload --host 0.0.0.0 --port 8000
```

### 📋 Quick Reference

#### Common Commands
```bash
# Activate environment
cd backend && source venv/bin/activate

# Run tests
pytest tests/ -v

# Start API server
uvicorn src.api:app --reload

# Check Ollama
ollama list

# View logs
tail -f logs/production.log
```

#### Troubleshooting
- **Import errors**: Check virtual environment is activated
- **Ollama errors**: Ensure Ollama is running with `ollama serve`
- **Permission errors**: Check file permissions
- **Port 8000 in use**: Change port in .env file

---

**🎊 Congratulations! Your development environment is ready!**

**Next step**: Dive into [Implementation Plan](../documentation/implementation-plan.md) and start building!

---

## 📞 Getting Help

### If Something Goes Wrong

1. **Check the error message carefully**
2. **Review each step in this guide**
3. **Search existing issues**
4. **Ask for help with specific error messages**

### Common Issues

**Issue**: `ModuleNotFoundError: No module named 'dspy'`
**Solution**: Ensure virtual environment is activated

**Issue**: `ollama: command not found`
**Solution**: Install Ollama following Step 5

**Issue**: `port 8000 is already in use`
**Solution**: Change API_PORT in .env file

### Contact Information
- **Documentation**: Check [FAQ](../resources/faq.md)
- **Issues**: Search existing issues first
- **Community**: Join our development channel

**Happy coding! 🚀**