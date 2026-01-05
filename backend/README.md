# Open-Instruct

An AI-powered educational content generation engine that creates structured learning objectives and quizzes based on Bloom's Taxonomy. Built with DSPy for structured LLM prompting and FastAPI for REST API functionality.

## Features

- **Structured Learning Objectives**: Automatically generates learning objectives organized by Bloom's Taxonomy levels
- **Quiz Generation**: Creates assessment questions aligned with learning objectives
- **Multiple LLM Providers**: Supports Ollama, OpenAI, and Anthropic
- **FastAPI REST API**: Clean, well-documented endpoints for integration
- **SQLite Persistence**: Built-in database for content storage
- **Intelligent Caching**: Reduces API calls and improves performance

## Prerequisites

- **Python 3.11+** - Required for project compatibility
- **Ollama** - Local LLM server (recommended for development)
- **pip** - Python package manager

## Installation

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Setup Ollama (Recommended)

Ollama provides free, local LLM inference. Perfect for development and testing.

```bash
# Install Ollama (if not already installed)
# Visit: https://ollama.ai/download

# Pull the recommended model
ollama pull deepseek-r1:1.5b

# Verify installation
ollama list
```

**Alternative Models**:
- `ollama pull llama3.2` - More capable, requires more resources
- `ollama pull mistral` - Good balance of speed and quality

## Configuration

Set up your environment variables:

```bash
# Copy the example environment file
cp .env.example .env

# Edit .env with your configuration
```

### Environment Variables

```bash
# LLM Provider Configuration
LLM_PROVIDER=ollama  # Options: ollama, openai, anthropic
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=deepseek-r1:1.5b

# Optional: OpenAI Configuration
# OPENAI_API_KEY=your_key_here
# OPENAI_MODEL=gpt-4

# Optional: Anthropic Configuration
# ANTHROPIC_API_KEY=your_key_here
# ANTHROPIC_MODEL=claude-3-sonnet-20240229

# Application Settings
PORT=8000
DEBUG=false
LOG_LEVEL=info
```

## Usage

### CLI Usage

Generate learning objectives directly from the command line:

```bash
# Generate objectives for a topic
python -m src.cli generate "Python decorators" \
  --context "for intermediate Python developers" \
  --count 5 \
  --provider ollama

# Generate with custom bloom levels
python -m src.cli generate "REST APIs" \
  --levels "understand,application" \
  --provider ollama
```

### API Usage

Start the FastAPI server:

```bash
# Development server with auto-reload
uvicorn src.api.main:app --reload --port 8000

# Production server
uvicorn src.api.main:app --host 0.0.0.0 --port 8000
```

#### API Endpoints

**Health Check**
```bash
curl http://localhost:8000/health
```

**Generate Learning Objectives**
```bash
curl -X POST http://localhost:8000/objectives \
  -H "Content-Type: application/json" \
  -d '{
    "topic": "Machine Learning Basics",
    "context": "for data science beginners",
    "count_per_level": 3
  }'
```

**Generate Quiz**
```bash
curl -X POST http://localhost:8000/quiz \
  -H "Content-Type: application/json" \
  -d '{
    "topic": "Python Functions",
    "context": "intermediate developers",
    "question_count": 5
  }'
```

**Interactive API Documentation**
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Project Structure

```
backend/
├── src/
│   ├── api/
│   │   ├── main.py          # FastAPI application
│   │   └── schemas.py       # Pydantic models
│   ├── core/
│   │   ├── models.py        # Data models
│   │   └── config.py        # Configuration
│   ├── modules/
│   │   ├── assessor.py      # Bloom's taxonomy assessment
│   │   └── generator.py     # Content generation
│   └── cli.py               # Command-line interface
├── tests/
│   ├── unit/                # Unit tests
│   ├── integration/         # Integration tests
│   └── golden/              # Golden set tests
└── requirements.txt         # Python dependencies
```

## Troubleshooting

### Ollama Connection Issues

**Problem**: `Connection refused` or `Cannot connect to Ollama`

**Solutions**:
1. Ensure Ollama is running: `ollama serve`
2. Check Ollama is accessible: `curl http://localhost:11434/api/tags`
3. Verify model is pulled: `ollama list`
4. Check firewall settings aren't blocking port 11434

### Python Import Errors

**Problem**: `ModuleNotFoundError: No module named 'src'`

**Solutions**:
1. Ensure you're in the `backend/` directory
2. Install package in editable mode: `pip install -e .`
3. Check Python version: `python --version` (must be 3.11+)

### API Server Won't Start

**Problem**: `Address already in use` or port conflicts

**Solutions**:
1. Check if port is in use: `lsof -i :8000`
2. Kill existing process: `kill -9 <PID>`
3. Use different port: `uvicorn src.api.main:app --port 8001`

### Slow Response Times

**Problem**: API requests take too long

**Solutions**:
1. Use smaller Ollama model: `ollama pull phi3`
2. Enable caching in `.env`: `CACHE_ENABLED=true`
3. Reduce `count_per_level` in requests
4. Check Ollama resources: `ollama ps`

### DSPy Errors

**Problem**: DSPy configuration or LLM errors

**Solutions**:
1. Verify `LLM_PROVIDER` is set correctly in `.env`
2. Check API keys for OpenAI/Anthropic if using those providers
3. Test LLM directly: `ollama run deepseek-r1:1.5b "test"`
4. Review logs: `tail -f logs/open_instruct.log`

### Test Failures

**Problem**: Tests failing with assertion errors

**Solutions**:
1. Ensure test environment is set up: `source .env.test`
2. Run specific test with verbose output: `pytest tests/unit/test_assessor.py -v`
3. Check Ollama is running before integration tests
4. Update golden set if expected behavior changed: `python tests/update_golden.py`

## Development

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test file
pytest tests/unit/test_assessor.py

# Run integration tests only
pytest tests/integration/
```

## License

MIT License - see LICENSE file for details

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Run tests and ensure they pass
6. Submit a pull request
