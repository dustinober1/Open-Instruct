# 🚀 Ollama Setup Guide: Free Local LLM

**Version**: 1.0.0
**Last Updated**: 2025-01-05

---

## 🎯 Overview

Ollama provides free, local access to LLMs without API costs. This guide helps you set up Ollama with the recommended models for Open-Instruct.

### Why Choose Ollama?
- ✅ **Completely free** - No API costs
- ✅ **Private** - Runs locally on your machine
- ✅ **Offline capable** - Works without internet
- ✅ **Educational** - Great for learning AI concepts
- ✅ **Multiple models** - Choose from various open-source models

---

## 🛠️ Installation

### Option 1: Homebrew (macOS - Recommended)
```bash
# Install via Homebrew
brew install ollama

# Start Ollama service (runs in background)
brew services start ollama
```

### Option 2: Direct Download

#### macOS
```bash
# Download macOS app
curl -L https://ollama.ai/download/Ollama-darwin.zip -o ollama-darwin.zip
unzip ollama-darwin.zip
sudo mv Ollama.app /Applications/
```

#### Windows
```powershell
# Download Windows app
Invoke-WebRequest -Uri "https://ollama.ai/download/OllamaSetup.exe" -OutFile "OllamaSetup.exe"
.\OllamaSetup.exe
```

#### Linux
```bash
# Download and install
curl -fsSL https://ollama.ai/install.sh | sh

# Start service
sudo systemctl start ollama
sudo systemctl enable ollama
```

### Option 3: Docker
```bash
# Pull and run Ollama Docker container
docker run -d -p 11434:11434 --name ollama ollama/ollama

# Verify it's running
docker ps | grep ollama
```

---

## 🤖 Model Selection

### Recommended Models for Open-Instruct

| Model | Size | Quality | Speed | Best For |
|-------|------|---------|-------|----------|
| **deepseek-r1:1.5b** | 1.5B | Good | Fast | **Recommended** - Balance of quality and speed |
| **deepseek-r1:7b** | 7B | Very Good | Medium | Better quality for complex tasks |
| **mistral:7b** | 7B | Very Good | Medium | General purpose, reliable |
| **llama3:8b** | 8B | Excellent | Medium | High quality, well-supported |

### Install Recommended Models

```bash
# Always install this first (recommended for project)
ollama pull deepseek-r1:1.5b

# Optional: Upgrade to better quality models
ollama pull deepseek-r1:7b     # Better quality
ollama pull mistral:7b         # Alternative option
ollama pull llama3:8b          # High quality
```

---

## 🔧 Configuration

### Basic Verification
```bash
# Check Ollama is running
ollama list

# Expected output if working:
# NAME            ID              SIZE    MODIFIED
# deepseek-r1:1.5b abc123  2.1 GB    2 hours ago
```

### Environment Configuration
```bash
# Create or update .env file
cat >> .env << EOF

# Ollama Configuration
OLLAMA_HOST=http://localhost:11434
OLLAMA_MODEL=deepseek-r1:1.5b
OLLAMA_TIMEOUT=30
EOF
```

### Configuration File (Advanced)
Create `config/ollama.yaml`:
```yaml
# Ollama Configuration
ollama:
  host: "http://localhost:11434"
  timeout: 30
  model: "deepseek-r1:1.5b"
  available_models:
    - deepseek-r1:1.5b
    - deepseek-r1:7b
    - mistral:7b
  default_model: "deepseek-r1:1.5b"
```

---

## 🧪 Testing Setup

### Test Basic Functionality
```python
# Test Ollama connection
import requests

try:
    response = requests.get("http://localhost:11434/api/tags")
    models = response.json()
    print("✅ Ollama is running")
    print(f"Available models: {len(models.get('models', []))}")
    for model in models['models']:
        print(f"  - {model['name']}")
except Exception as e:
    print(f"❌ Ollama connection failed: {e}")
```

### Test Model Generation
```python
# Test model generation
import requests

def test_ollama_generation():
    prompt = "Generate a learning objective about Python programming at the 'understand' level of Bloom's Taxonomy."

    payload = {
        "model": "deepseek-r1:1.5b",
        "prompt": prompt,
        "stream": False
    }

    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json=payload
        )
        if response.status_code == 200:
            result = response.json()
            print("✅ Model generation successful")
            print(f"Response length: {len(result.get('response', ''))}")
            return True
        else:
            print(f"❌ Generation failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

# Run test
test_ollama_generation()
```

---

## 📊 Performance Optimization

### System Requirements
```bash
# Check system resources
python -c "
import psutil
import GPUtil

print('System Resources:')
print(f'CPU Cores: {psutil.cpu_count()}')
print(f'Memory: {psutil.virtual_memory().total / (1024**3):.1f} GB')
if GPUtil.getGPUs():
    gpu = GPUtil.getGPUs()[0]
    print(f'GPU: {gpu.name}, Memory: {gpu.memoryTotal} MB')
else:
    print('GPU: Not available')
"
```

### Model Selection Guidelines

| Your System | Recommended Model |
|-------------|-------------------|
| **8GB RAM, 4 CPU cores** | deepseek-r1:1.5b |
| **16GB RAM, 8 CPU cores** | deepseek-r1:7b |
| **32GB RAM, 16+ CPU cores** | llama3:8b or mistral:7b |

### Performance Testing
```bash
# Test model performance
ollama run deepseek-r1:1.5b "Generate 3 learning objectives about machine learning"

# Test multiple models for comparison
echo "Testing different models for educational content generation..."
for model in deepseek-r1:1.5b mistral:7b; do
    echo "Testing $model..."
    start_time=$(date +%s%N)
    ollama run $model "Generate 2 learning objectives about data science"
    end_time=$(date +%s%N)
    echo "Time: $((($end_time - $start_time) / 1000000))ms"
    echo "---"
done
```

---

## 🔍 Troubleshooting

### Common Issues

#### Issue: "ollama: command not found"
**Solution**:
```bash
# Check installation path
which ollama

# If not found, reinstall
# macOS: brew reinstall ollama
# Linux: curl -fsSL https://ollama.ai/install.sh | sh
```

#### Issue: "Connection refused"
**Solution**:
```bash
# Check if Ollama is running
ps aux | grep ollama

# Start Ollama service
# macOS: brew services start ollama
# Linux: sudo systemctl start ollama
# Or run: ollama serve
```

#### Issue: Model download fails
**Solution**:
```bash
# Check internet connection
ping google.com

# Clear download cache and retry
ollama rm deepseek-r1:1.5b
ollama pull deepseek-r1:1.5b

# Use alternative mirror (if available)
export OLLAMA_HOST=https://mirror.example.com
```

#### Issue: Poor performance
**Solution**:
```bash
# Monitor system resources
htop  # or top

# Reduce model size
ollama pull deepseek-r1:1.5b  # Smaller model

# Check for background processes
ps aux | grep -v grep | grep ollama
```

### Advanced Troubleshooting

#### Debug Mode
```bash
# Run Ollama in debug mode
ollama serve --debug

# Check logs
tail -f ~/.ollama/logs/ollama.log
```

#### Port Conflicts
```bash
# Check what's using port 11434
lsof -i :11434

# Change Ollama port (if needed)
export OLLAMA_HOST=http://localhost:11435
ollama serve --port 11435
```

---

## 🔄 Model Management

### List Installed Models
```bash
# List all models
ollama list

# Model details
ollama list --details
```

### Remove Models
```bash
# Remove specific model
ollama rm deepseek-r1:7b

# Remove all models (reinstall later)
ollama list --format '{{.Name}}' | xargs -I {} ollama rm {}
```

### Update Models
```bash
# Update existing model
ollama pull deepseek-r1:1.5b  # Reinstalls latest version

# Check for updates
ollama list --format '{{.Name}} {{.Size}} {{.Modified}}'
```

---

## 📋 Best Practices

### For Development
1. **Start small**: Use `deepseek-r1:1.5b` for initial development
2. **Test thoroughly**: Verify outputs before switching to larger models
3. **Cache responses**: Use the built-in caching system
4. **Monitor resources**: Check CPU/RAM usage regularly

### For Production
1. **Choose appropriate model**: Match model size to available resources
2. **Set up monitoring**: Track response times and success rates
3. **Implement fallbacks**: Have smaller model ready for high load
4. **Regular updates**: Keep models up to date for security/patches

### Cost Optimization
- **Free**: No API costs, only electricity
- **Efficient**: Small models work well for educational content
- **Scalable**: Upgrade models as needed without cost changes

---

## 🎯 Next Steps

### After Successful Setup
1. **Test with Open-Instruct**:
   ```bash
   # Navigate to project directory
   cd /path/to/Open_Instruct/backend

   # Run test
   python -c "import examples.ollama_test as test; test.run()"
   ```

2. **Configure Open-Instruct**:
   ```bash
   # Set environment variable
   export LLM_PROVIDER=ollama
   export LLM_MODEL=deepseek-r1:1.5b

   # Test configuration
   python scripts/test_llm_connection.py
   ```

3. **Start Development**:
   - Follow Week 2 implementation plan
   - Use the Ollama-optimized DSPy examples
   - Test with your chosen model

### Switching Models
```bash
# To switch models:
export LLM_MODEL=mistral:7b  # or llama3:8b
ollama pull $LLM_MODEL       # Ensure model is installed

# Test new model
python scripts/test_model.py
```

---

## 📞 Getting Help

### Common Questions
**Q: "Which model should I choose?"**
A: Start with `deepseek-r1:1.5b` - it's optimized for speed and works well on most systems.

**Q: "Can I use Ollama offline?"**
A: Yes! Once models are downloaded, Ollama works completely offline.

**Q: "How much RAM do I need?"**
A: Minimum 8GB for 1.5B model, 16GB+ for larger models.

### Community Support
- **Discord**: Join Ollama community server
- **GitHub**: Report issues at github.com/ollama/ollama
- **Documentation**: Check https://github.com/ollama/ollama/tree/main/docs

---

**Ready to start with Ollama?** Move on to [OpenAI Setup](openai-setup.md) or [Anthropic Setup](anthropic-setup.md) to compare options, or continue with [Provider Comparison](provider-comparison.md).

**Next step**: [OpenAI Setup Guide](openai-setup.md) 💰