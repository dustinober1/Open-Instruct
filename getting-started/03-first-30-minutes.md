# ⏱️ First 30 Minutes: Quick Orientation

**Version**: 1.0.0
**Last Updated**: 2025-01-05

---

## 🎯 Mission: Get Oriented in 30 Minutes

This guide helps you quickly understand the Open-Instruct project and verify your setup. Complete these steps in order.

---

## ✅ Step 1: Read This Guide (2 minutes)

### What You're Building
- **AI-powered educational content generator**
- **Uses Bloom's Taxonomy for learning objectives**
- **Local LLM (no API costs)**
- **FastAPI web interface**

### Key Technologies
- **Python + FastAPI** (Backend)
- **DSPy** (AI prompting)
- **SQLite** (Database)
- **Ollama** (Local LLM)
- **TDD** (Testing)

### Project Structure
```
Open_Instruct/
├── 📚 README.md                 # You're here!
├── 🚀 getting-started/          # Onboarding materials
├── 📋 documentation/           # Core implementation docs
├── 🎯 examples/               # Practical examples
└── 📖 resources/             # Additional resources
```

---

## ✅ Step 2: Understand the Big Picture (3 minutes)

### Read: Project Overview
Open [01-project-overview.md](01-project-overview.md) and read:
- What is Open-Instruct?
- How it works (the diagram)
- Core components
- Success criteria

**Key Question to Answer**: *What will I be building?*

### Read: Prerequisites
Open [02-prerequisites.md](02-prerequisites.md) and verify:
- You have the required knowledge
- Tools are installed
- You understand what we'll teach you

**Key Question to Answer**: *Am I ready to start?*

---

## ✅ Step 3: Set Up Your Environment (10 minutes)

### Quick Environment Check
```bash
# 1. Check Python
python --version  # Should be 3.9+

# 2. Check Git
git --version

# 3. Navigate to project (if already cloned)
cd /path/to/Open_Instruct
ls -la  # Should see documentation files

# 4. If not cloned yet:
git clone <repository-url>
cd Open_Instruct
```

### Quick Setup (If Not Done)
```bash
# Create backend structure
mkdir -p backend/src/{core,modules} tests logs

# Set up virtual environment
cd backend
python -m venv venv
source venv/bin/activate  # macOS/Linux

# Install core dependencies
pip install dspy-ai pydantic fastapi uvicorn pytest

# Verify installation
python -c "import dspy; print('DSPy version:', dspy.__version__)"
```

---

## ✅ Step 4: Verify Ollama Setup (5 minutes)

### Check if Ollama is Installed
```bash
# Check if Ollama is running
ollama list
```

### If Ollama is Not Installed
```bash
# Option 1: Install via Homebrew (macOS)
brew install ollama

# Option 2: Download from website
# Visit: https://ollama.ai/download

# Option 3: Docker (advanced)
docker run -d -p 11434:11434 --name ollama ollama/ollama
```

### Pull the Model
```bash
# Pull DeepSeek-R1 model (required for the project)
ollama pull deepseek-r1:1.5b

# Verify installation
ollama list  # Should show deepseek-r1:1.5b
```

---

## ✅ Step 5: First Test (5 minutes)

### Create a Simple Test File
```bash
# Go to backend directory
cd backend

# Create a simple test
cat > test_hello.py << 'EOF'
def test_hello_world():
    """Test that basic Python works"""
    assert 1 + 1 == 2

def test_imports():
    """Test that all packages can be imported"""
    import dspy
    import pydantic
    import fastapi
    import uvicorn
    import pytest
    print("✅ All imports successful!")

if __name__ == "__main__":
    test_hello_world()
    test_imports()
    print("✅ All tests passed!")
EOF
```

### Run the Test
```bash
# Run the test
python test_hello.py

# Or with pytest
pytest test_hello.py -v
```

### Expected Output
```
✅ All imports successful!
✅ All tests passed!
```

If this works, your environment is ready!

---

## ✅ Step 6: Review Next Steps (5 minutes)

### Completed Checklist
- [ ] Read this guide
- [ ] Understand the big picture
- [ ] Set up environment
- [ ] Verify Ollama
- [ ] Run first test

### What's Next?

**Option A: Full Implementation**
1. Read [Implementation Plan](../documentation/implementation-plan.md)
2. Follow Week 1, Day 1 instructions
3. Start building the system step by step

**Option B: Quick Spike**
1. Try a simple DSPy example first
2. Test LLM connection
3. Generate your first educational content

**Option C: Learn More**
1. Read [DSPy Prompt Strategy](../documentation/dspy-prompt-strategy.md)
2. Explore [Bloom's Taxonomy](../documentation/blooms-taxonomy.md)
3. Watch tutorials on FastAPI

---

## 🚀 You're Ready! 🎉

### Congratulations! You've completed:
- ✅ Project orientation
- ✅ Environment setup
- ✅ Tool verification
- ✅ First test

### Next Steps (Choose Your Path)

#### Path 1: Follow the Plan
```bash
# Start with the official implementation plan
cat documentation/implementation-plan.md
```

#### Path 2: Try Something First
```bash
# Generate your first educational objective
# We'll show you how in the next steps
```

#### Path 3: Get Help
- Check [FAQ](../resources/faq.md)
- Read [Troubleshooting](../examples/troubleshooting.md)
- Ask questions in the project channel

### Pro Tips for Success
1. **Take notes** - Document what you learn
2. **Ask questions** - No such thing as a silly question
3. **Follow TDD** - Write tests first, then code
4. **Commit often** - Use Git to track your progress
5. **Celebrate wins** - Each milestone is an achievement!

---

## 📞 Quick Reference

### Need Help?
- **Documentation**: Check specific guides
- **Examples**: See `examples/` folder
- **Community**: Ask in project channel
- **Issues**: Search existing issues first

### Key Commands
```bash
# Environment
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Testing
pytest tests/ -v

# Ollama
ollama list
ollama pull deepseek-r1:1.5b

# Git
git status
git add .
git commit -m "your message"
```

---

**You've completed your first 30 minutes! Great job! 🎉**

**Next**: [Quick Setup Guide](04-quick-setup-guide.md) or dive into [Implementation Plan](../documentation/implementation-plan.md)