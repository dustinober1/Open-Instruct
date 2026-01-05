# 🔧 Backend Troubleshooting Guide

**Comprehensive troubleshooting for Open-Instruct Backend**

---

## 🚀 Quick Diagnosis

### Quick Health Check

```bash
# Run this quick diagnostic script
#!/bin/bash
echo "=== Open-Instruct Backend Health Check ==="

# 1. Check Python version
echo -n "Python version: "
python --version

# 2. Check virtual environment
echo -n "Virtual environment: "
if [[ "$VIRTUAL_ENV" != "" ]]; then
  echo "✅ Activated ($VIRTUAL_ENV)"
else
  echo "❌ Not activated"
fi

# 3. Check dependencies
echo -n "Dependencies: "
if pip list | grep -q "fastapi"; then
  echo "✅ Installed"
else
  echo "❌ Missing"
fi

# 4. Check Ollama
echo -n "Ollama: "
if curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
  echo "✅ Running"
else
  echo "❌ Not running"
fi

# 5. Check environment file
echo -n "Environment file: "
if [ -f .env ]; then
  echo "✅ Present"
else
  echo "❌ Missing"
fi

# 6. Check data directory
echo -n "Data directory: "
if [ -d data ]; then
  echo "✅ Present"
else
  echo "❌ Missing (create with: mkdir data)"
fi

echo "=== End Health Check ==="
```

Save as `check_health.sh`, make executable, and run:
```bash
chmod +x check_health.sh
./check_health.sh
```

---

## 🔍 Common Error Categories

### 1. Installation & Setup Issues

#### Error: "python: command not found"

**Symptoms:**
```bash
python: command not found
```

**Diagnosis:**
```bash
# Check if python3 exists
python3 --version

# Check available Python versions
which -a python python3
```

**Solutions:**

**Option 1: Use python3 instead of python**
```bash
# Always use python3
python3 -m venv venv
source venv/bin/activate
```

**Option 2: Create python alias**
```bash
# Add to ~/.bashrc or ~/.zshrc
alias python='python3'
alias pip='pip3'

# Reload shell
source ~/.bashrc  # or ~/.zshrc
```

**Option 3: Install Python**
```bash
# macOS
brew install python

# Ubuntu/Debian
sudo apt-get install python3 python3-pip python3-venv

# Windows
# Download from https://www.python.org/downloads/
```

---

#### Error: "Failed to create virtual environment"

**Symptoms:**
```bash
Error: Command '[(...)]' returned non-zero exit status 1
```

**Solutions:**

**Option 1: Ensure python3-venv is installed**
```bash
# Ubuntu/Debian
sudo apt-get install python3-venv

# macOS (should be included)
# Reinstall Python if missing
brew reinstall python
```

**Option 2: Use virtualenv instead**
```bash
pip install virtualenv
virtualenv venv
source venv/bin/activate
```

**Option 3: Use venv module directly**
```bash
python3 -m venv --without-pip venv
source venv/bin/activate
curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
python get-pip.py
```

---

#### Error: "ModuleNotFoundError: No module named 'fastapi'"

**Symptoms:**
```
ModuleNotFoundError: No module named 'fastapi'
```

**Diagnosis:**
```bash
# Check if virtual environment is activated
echo $VIRTUAL_ENV

# Check if package is installed
pip list | grep fastapi
```

**Solutions:**

**Option 1: Activate virtual environment**
```bash
# Activate virtual environment
source venv/bin/activate  # macOS/Linux
# or
venv\Scripts\activate  # Windows

# Verify activation
which python  # Should point to venv/bin/python
```

**Option 2: Reinstall dependencies**
```bash
# Ensure virtual environment is activated
source venv/bin/activate

# Reinstall all dependencies
pip install -r requirements.txt

# Verify installation
pip list | grep fastapi
```

**Option 3: Upgrade pip first**
```bash
# Upgrade pip
pip install --upgrade pip

# Then install requirements
pip install -r requirements.txt
```

---

### 2. LLM Provider Issues

#### Error: Ollama Connection Refused

**Symptoms:**
```
ConnectionError: Failed to connect to Ollama at http://localhost:11434
Service Unavailable: Ollama is not accessible
```

**Diagnosis:**
```bash
# Test Ollama connection
curl http://localhost:11434/api/tags

# Check if Ollama is running
ps aux | grep ollama

# Check port 11434
lsof -i :11434
```

**Solutions:**

**Option 1: Start Ollama**
```bash
# macOS
brew services start ollama

# Linux
sudo systemctl start ollama

# Or run directly
ollama serve
```

**Option 2: Restart Ollama**
```bash
# macOS
brew services restart ollama

# Linux
sudo systemctl restart ollama

# Or kill and restart
killall ollama
ollama serve
```

**Option 3: Reinstall Ollama**
```bash
# macOS
brew reinstall ollama

# Verify installation
ollama --version
```

**Option 4: Check for port conflicts**
```bash
# Check what's using port 11434
lsof -i :11434

# Kill conflicting process
kill -9 <PID>
```

---

#### Error: "Model not found: deepseek-r1:1.5b"

**Symptoms:**
```
Error: model 'deepseek-r1:1.5b' not found
```

**Diagnosis:**
```bash
# List installed models
ollama list

# Check for specific model
ollama list | grep deepseek-r1
```

**Solutions:**

**Option 1: Pull the model**
```bash
# Pull recommended model
ollama pull deepseek-r1:1.5b

# Verify installation
ollama list
```

**Option 2: Use alternative model**
```bash
# Pull different model
ollama pull mistral:7b

# Update .env file
echo "OLLAMA_MODEL=mistral:7b" >> .env
```

**Option 3: Reinstall model**
```bash
# Remove corrupted model
ollama rm deepseek-r1:1.5b

# Pull again
ollama pull deepseek-r1:1.5b
```

---

#### Error: OpenAI API Errors

**Symptoms:**
```
AuthenticationError: Incorrect API key provided
RateLimitError: Rate limit exceeded
```

**Diagnosis:**
```bash
# Check if API key is set
echo $OPENAI_API_KEY

# Test API key
curl https://api.openai.com/v1/models \
  -H "Authorization: Bearer $OPENAI_API_KEY"
```

**Solutions:**

**Option 1: Verify API key in .env**
```bash
# Check .env file
cat .env | grep OPENAI

# Ensure correct format
echo "OPENAI_API_KEY=sk-..." > .env
```

**Option 2: Set API key in shell**
```bash
# Export API key
export OPENAI_API_KEY="sk-your-key-here"

# Add to ~/.bashrc or ~/.zshrc for persistence
echo 'export OPENAI_API_KEY="sk-your-key-here"' >> ~/.bashrc
source ~/.bashrc
```

**Option 3: Handle rate limits**
```bash
# Upgrade to paid tier if on free tier
# Or implement request queuing
# See src/core/error_handlers.py for retry logic
```

---

### 3. API Server Issues

#### Error: "Address already in use: port 8000"

**Symptoms:**
```
OSError: [Errno 48] Address already in use
```

**Diagnosis:**
```bash
# Find process using port 8000
lsof -i :8000

# List all Python processes
ps aux | grep python | grep uvicorn
```

**Solutions:**

**Option 1: Kill existing process**
```bash
# Get PID from lsof output
lsof -i :8000
# Output: python  12345 user ... TCP *:8000 (LISTEN)

# Kill the process
kill 12345

# Or force kill
kill -9 12345
```

**Option 2: Use different port**
```bash
# Start on port 8001
uvicorn src.api.main:app --port 8001
```

**Option 3: Kill all uvicorn processes**
```bash
# Kill all uvicorn processes
pkill -f uvicorn

# Or
killall uvicorn
```

---

#### Error: "ImportError: cannot import name 'X' from 'Y'"

**Symptoms:**
```
ImportError: cannot import name 'Architect' from 'src.modules.architect'
```

**Diagnosis:**
```bash
# Check if file exists
ls -la src/modules/architect.py

# Test import
python -c "from src.modules.architect import Architect"

# Check PYTHONPATH
echo $PYTHONPATH
```

**Solutions:**

**Option 1: Run from backend directory**
```bash
# Ensure you're in backend directory
cd backend

# Test import again
python -c "from src.modules.architect import Architect; print('✅ Import successful')"
```

**Option 2: Add to PYTHONPATH**
```bash
# Add project root to PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

# Make persistent
echo 'export PYTHONPATH="${PYTHONPATH}:~/Projects/Open_Instruct/backend"' >> ~/.bashrc
source ~/.bashrc
```

**Option 3: Use python -m syntax**
```bash
# Use -m flag to run as module
python -m src.api.main

# Or for tests
python -m pytest tests/unit/
```

---

### 4. Performance Issues

#### Issue: Slow generation times

**Symptoms:**
- API requests take 30+ seconds
- Generation timeouts (HTTP 504)
- Poor user experience

**Diagnosis:**
```bash
# Check system resources
top
# or
htop

# Check Ollama generation speed
time ollama run deepseek-r1:1.5b "Generate 3 learning objectives"

# Check API logs
tail -f logs/production.log | grep "processing_time_ms"
```

**Solutions:**

**Option 1: Use smaller/faster model**
```bash
# Pull smaller model
ollama pull deepseek-r1:1.5b

# Update .env
echo "OLLAMA_MODEL=deepseek-r1:1.5b" >> .env
```

**Option 2: Increase timeout**
```bash
# Update .env
echo "REQUEST_TIMEOUT=120" >> .env  # 60 seconds → 120 seconds
```

**Option 3: Enable caching**
```bash
# Ensure cache is enabled in .env
echo "CACHE_TTL=604800" >> .env  # 7 days

# Cache is implemented in src/api/main.py
# Check cache_key generation
```

**Option 4: Optimize system resources**
```bash
# Close unnecessary applications
# Check available memory
free -h  # Linux
vm_stat  # macOS

# Restart Ollama if memory leak suspected
brew services restart ollama
```

---

#### Issue: High memory usage

**Symptoms:**
- Ollama using 4GB+ RAM
- System slowdowns
- Out of memory errors

**Diagnosis:**
```bash
# Check memory usage
ps aux | grep ollama

# Check overall system memory
free -h  # Linux
# or
vm_stat  # macOS
```

**Solutions:**

**Option 1: Use smaller model**
```bash
# Remove large models
ollama rm llama3:8b
ollama rm deepseek-r1:7b

# Use smallest model
ollama pull deepseek-r1:1.5b
```

**Option 2: Restart Ollama**
```bash
# Restart Ollama to free memory
brew services restart ollama  # macOS
sudo systemctl restart ollama  # Linux
```

**Option 3: Limit concurrent requests**
```bash
# Reduce number of workers
uvicorn src.api.main:app --workers 1  # Instead of 4
```

---

### 5. Test Failures

#### Error: "Tests failing with import errors"

**Symptoms:**
```
ImportError: No module named 'src'
```

**Diagnosis:**
```bash
# Check current directory
pwd

# Check if running from backend directory
ls -la src/

# Test import
python -c "import src"
```

**Solutions:**

**Option 1: Run tests from backend directory**
```bash
# Ensure you're in backend directory
cd /path/to/Open_Instruct/backend

# Run tests
pytest
```

**Option 2: Install project in development mode**
```bash
# Create setup.py if missing
cat > setup.py << 'EOF'
from setuptools import setup, find_packages

setup(
    name='open-instruct',
    version='1.0.0',
    packages=find_packages(),
)
EOF

# Install in development mode
pip install -e .
```

**Option 3: Update PYTHONPATH**
```bash
# Add backend directory to PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

# Run tests
pytest
```

---

#### Error: "Coverage below 85% threshold"

**Symptoms:**
```
FAILED  Required test coverage of 85% not reached. Actual: 72.3%
```

**Solutions:**

**Option 1: See what's not covered**
```bash
# Run coverage with detailed report
pytest --cov=src --cov-report=term-missing

# Look for lines marked with ">>>>>"
```

**Option 2: Generate HTML coverage report**
```bash
# Generate detailed HTML report
pytest --cov=src --cov-report=html

# Open report
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
```

**Option 3: Lower threshold temporarily**
```bash
# Edit pyproject.toml
# Change: "--cov-fail-under=85"
# To: "--cov-fail-under=70"

# Or pytest.ini
```

**Option 4: Write tests for uncovered code**
```bash
# Identify uncovered modules
# Add tests in tests/unit/ or tests/mocked/
# Follow TDD approach: Red → Green → Refactor
```

---

### 6. Database Issues

#### Error: "Database file not found"

**Symptoms:**
```
sqlite3.OperationalError: unable to open database file
```

**Diagnosis:**
```bash
# Check if data directory exists
ls -la data/

# Check .env database URL
cat .env | grep DATABASE_URL
```

**Solutions:**

**Option 1: Create data directory**
```bash
# Create data directory
mkdir -p data

# Verify creation
ls -la data/
```

**Option 2: Update DATABASE_URL in .env**
```bash
# Check current DATABASE_URL
cat .env | grep DATABASE_URL

# Update if path is incorrect
echo "DATABASE_URL=sqlite:///./data/open_instruct.db" >> .env
```

**Option 3: Create empty database**
```bash
# Create empty SQLite database
sqlite3 data/open_instruct.db ""

# Verify creation
ls -la data/open_instruct.db
```

---

## 🔧 Advanced Troubleshooting

### Debug Mode

Enable comprehensive debugging:

```bash
# Set environment variables
export LOG_LEVEL=DEBUG
export DSPY_LOG_LEVEL=DEBUG

# Run server with debug output
uvicorn src.api.main:app --reload --log-level debug
```

Check logs in real-time:
```bash
# Follow API logs
tail -f logs/production.log

# Follow Uvicorn logs
tail -f logs/uvicorn.log

# Or combine both
tail -f logs/*.log
```

---

### Circuit Breaker Issues

**Symptoms:**
```
HTTP 503 Service Unavailable
Error code: CIRCUIT_BREAKER_OPEN
```

**Diagnosis:**
```bash
# Check logs for circuit breaker events
grep -i "circuit breaker" logs/production.log

# Check error rate
grep -i "error" logs/production.log | tail -20
```

**Solutions:**

**Option 1: Wait for circuit breaker to reset**
```bash
# Circuit breaker resets after timeout (default 60 seconds)
# Wait 60 seconds and try again
```

**Option 2: Manually reset circuit breaker**
```bash
# Restart API server
# Circuit breaker state resets on restart
uvicorn src.api.main:app --reload
```

**Option 3: Fix underlying issue**
```bash
# Check why failures are occurring
tail -50 logs/production.log

# Common causes:
# - Ollama not running
# - Model not available
# - Network issues
# - Resource exhaustion
```

---

### DSPy Configuration Issues

**Symptoms:**
```
DSPy configuration error
Invalid model configuration
```

**Diagnosis:**
```bash
# Test DSPy configuration
python -c "
from src.core.dspy_client import configure_dspy, get_model_info
configure_dspy()
print(get_model_info())
"
```

**Solutions:**

**Option 1: Check DSPy configuration**
```bash
# Check src/core/dspy_client.py
# Verify configure_dspy() function

# Test configuration
python -c "from src.core.dspy_client import configure_dspy; configure_dspy()"
```

**Option 2: Reset DSPy configuration**
```bash
# Clear DSPy cache (if any)
rm -rf .cache/

# Reconfigure
python -c "from src.core.dspy_client import configure_dspy; configure_dspy()"
```

**Option 3: Check environment variables**
```bash
# Verify all required environment variables are set
env | grep -E "OLLAMA|OPENAI|ANTHROPIC|DSPY"
```

---

## 📊 Performance Monitoring

### Monitor API Performance

```bash
# Script to monitor response times
#!/bin/bash
while true; do
  echo "=== $(date) ==="
  curl -w "\nTime Total: %{time_total}s\n" \
    -X POST http://localhost:8000/api/v1/generate/objectives \
    -H "Content-Type: application/json" \
    -d '{"topic":"test","target_audience":"testers","num_objectives":3}' \
    -o /dev/null -s
  sleep 5
done
```

### Monitor System Resources

```bash
# Check CPU and memory usage
top -o cpu -n 5

# Or use htop for interactive monitoring
htop

# Check disk usage
df -h

# Check Ollama resources
ps aux | grep ollama
```

---

## 🚨 Emergency Procedures

### Complete System Reset

If everything is failing:

```bash
#!/bin/bash
# Emergency reset script

echo "=== Emergency Reset ==="

# 1. Stop all processes
echo "Stopping all processes..."
pkill -f uvicorn
killall ollama 2>/dev/null || true

# 2. Remove virtual environment
echo "Removing virtual environment..."
rm -rf venv/

# 3. Create new virtual environment
echo "Creating new virtual environment..."
python3 -m venv venv
source venv/bin/activate

# 4. Reinstall dependencies
echo "Reinstalling dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# 5. Restart Ollama
echo "Restarting Ollama..."
brew services restart ollama  # macOS
# or
sudo systemctl restart ollama  # Linux

# 6. Wait for Ollama to start
sleep 5

# 7. Test Ollama
echo "Testing Ollama..."
curl http://localhost:11434/api/tags

# 8. Start API server
echo "Starting API server..."
uvicorn src.api.main:app --reload

echo "=== Reset Complete ==="
```

Save as `emergency_reset.sh`, make executable, and run as last resort:
```bash
chmod +x emergency_reset.sh
./emergency_reset.sh
```

---

## 📞 Getting Help

### What to Include When Asking for Help

1. **System Information:**
   ```bash
   python --version
   pip --version
   uname -a  # Linux/macOS
   ```

2. **Error Messages:**
   - Full traceback
   - Error message
   - Steps to reproduce

3. **Environment:**
   ```bash
   cat .env  # Remove sensitive keys first!
   env | grep -E "OLLAMA|OPENAI|ANTHROPIC"
   ```

4. **Logs:**
   ```bash
   tail -50 logs/production.log
   tail -50 logs/error.log
   ```

5. **What You've Tried:**
   - List of attempted solutions
   - Results of diagnostic commands

### Useful Diagnostic Commands

```bash
# Complete system diagnostic
python -c "
import sys
import os
print(f'Python: {sys.version}')
print(f'Platform: {sys.platform}')
print(f'CWD: {os.getcwd()}')
print(f'PYTHONPATH: {os.environ.get(\"PYTHONPATH\", \"Not set\")}')
"

# Test all imports
python -c "
import fastapi
import dspy
import pydantic
import uvicorn
print('✅ All core imports successful')
"

# Test LLM connection
python -c "
from src.core.dspy_client import test_ollama_connection
result = test_ollama_connection()
print(f'Ollama Status: {result}')
"
```

---

## ✅ Prevention Tips

### Best Practices

1. **Always use virtual environment**
   ```bash
   source venv/bin/activate  # Before running any commands
   ```

2. **Keep dependencies updated**
   ```bash
   pip install --upgrade pip
   pip install --upgrade -r requirements.txt
   ```

3. **Run tests before committing**
   ```bash
   pytest --cov=src
   ```

4. **Check health before starting work**
   ```bash
   ./check_health.sh  # Create and run this script
   ```

5. **Monitor logs regularly**
   ```bash
   tail -f logs/production.log
   ```

6. **Commit .env.example, not .env**
   ```bash
   cp .env .env.example
   # Remove sensitive keys from .env.example
   git add .env.example
   ```

---

**Last Updated**: 2026-01-05
**Version**: 1.0.0

For additional help, see:
- [Main README](README.md)
- [Ollama Setup Guide](../examples/ollama-setup.md)
- [Error Scenarios](../documentation/error-scenarios.md)
