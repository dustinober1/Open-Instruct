# 📋 Prerequisites: What You Need to Know

**Version**: 1.0.0
**Last Updated**: 2025-01-05

---

## 🎯 Who This Is For

This project is designed for **junior developers** who want to learn AI/LLM integration while building a real application.

### Perfect If You Have
- **Basic Python programming** skills
- **Git fundamentals** (clone, commit, push)
- **Terminal/CLI** comfort
- **REST API** concepts understanding

### Welcome If You're New To
- **Test-Driven Development (TDD)** - We'll teach you!
- **FastAPI web framework** - We'll teach you!
- **DSPy AI framework** - We'll teach you!
- **SQLite databases** - We'll teach you!
- **Ollama local LLMs** - We'll set it up together!

---

## 🛠️ Required Knowledge

### ✅ Must Have (Fundamental)

#### 1. **Python Programming Basics**
```python
# You should understand:
# Variables, functions, classes
def greeting(name):
    return f"Hello, {name}!"

# Basic OOP
class Person:
    def __init__(self, name):
        self.name = name

    def say_hello(self):
        return greeting(self.name)
```

**Why you need this**: We'll build the entire system in Python. You'll need to understand classes, functions, and basic object-oriented concepts.

#### 2. **Git Fundamentals**
```bash
# You should be able to:
git clone <repository-url>
git add .
git commit -m "Your message"
git push
```

**Why you need this**: Version control is essential for collaboration and tracking your progress.

#### 3. **Terminal/CLI Basics**
```bash
# You should be comfortable with:
# Navigation
cd /path/to/directory
ls
mkdir new-folder

# File operations
cat file.txt
cp source.txt destination.txt
rm file.txt

# Environment management
python -m venv venv
source venv/bin/activate  # macOS/Linux
```

**Why you need this**: You'll spend time in the terminal setting up your environment and running commands.

#### 4. **REST API Concepts**
```json
// You should understand:
// HTTP methods
GET    /courses     // Retrieve data
POST   /courses     // Create new
PUT    /courses/1   // Update existing
DELETE /courses/1   // Delete

// JSON format
{
  "id": 1,
  "title": "Introduction to Python",
  "description": "Learn Python basics"
}
```

**Why you need this**: The project builds a REST API. You need to understand how web APIs work.

---

## 🎯 Helpful But Not Required (We'll Teach You)

### 1. **Test-Driven Development (TDD)**
```python
# We'll teach you this pattern:
# RED: Write failing test first
def test_addition():
    assert add(2, 3) == 5  # This test fails first

# GREEN: Write minimal code to pass
def add(a, b):
    return a + b  # Now the test passes

# REFACTOR: Improve code while tests pass
def add(a, b):
    """Add two numbers together."""
    return a + b
```

### 2. **FastAPI Web Framework**
```python
# We'll teach you FastAPI:
from fastapi import FastAPI

app = FastAPI()

@app.get("/hello/{name}")
def read_item(name: str):
    return {"message": f"Hello {name}"}
```

### 3. **DSPy AI Framework**
```python
# We'll teach you DSPy:
import dspy

class GenerateObjectives(dspy.Module):
    def __init__(self):
        self.generate = dspy.TypedPredictor(...)

    def forward(self, topic):
        return self.generate(topic=topic)
```

### 4. **SQLite Databases**
```sql
-- We'll teach you SQL:
CREATE TABLE courses (
    id INTEGER PRIMARY KEY,
    title TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO courses (title) VALUES ('Python Basics');
SELECT * FROM courses;
```

### 5. **Ollama Local LLMs**
```bash
# We'll help you set this up:
ollama pull deepseek-r1:1.5b
ollama list
```

---

## 🛠️ Tools to Install

### Step 1: Python (if not installed)

#### macOS
```bash
brew install python
```

#### Other Systems
- **Download from**: https://www.python.org/downloads/
- **Verify installation**: `python --version` or `python3 --version`

### Step 2: Git (if not installed)

#### macOS
```bash
brew install git
```

#### Windows
- **Download from**: https://git-scm.com/download/win

#### Verify installation
```bash
git --version
```

### Step 3: Code Editor (Recommended)

#### VS Code (Recommended)
1. **Download**: https://code.visualstudio.com/
2. **Install Python Extension**: Open VS Code, go to Extensions, search "Python"
3. **Recommended Extensions**:
   - Python (Microsoft)
   - Pylance (Microsoft)
   - GitLens (Microsoft)

#### Alternatives
- **PyCharm Community** (Free)
- **Sublime Text**
- **Vim/Neovim**

### Step 4: Git Configuration

```bash
# Set your name and email
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"

# Set up line endings (for macOS/Linux)
git config --global core.autocrlf input
```

---

## 🧪 Knowledge Check

### Quick Quiz

1. **Can you write a Python function that takes two numbers and returns their sum?**
   ```python
   def add_numbers(a, b):
       return a + b
   ```

2. **Can you navigate to a directory and list its contents?**
   ```bash
   cd /path/to/project
   ls -la
   ```

3. **Can you create a simple Git repository?**
   ```bash
   mkdir my-project
   cd my-project
   git init
   echo "# My Project" > README.md
   git add README.md
   git commit -m "Initial commit"
   ```

### If You're Unsure...

#### If Python is new to you:
- **Resource**: [Python for Everybody](https://www.py4e.com/)
- **Time**: 1-2 weeks to learn basics
- **Practice**: Complete the first 3 chapters

#### If Git is new to you:
- **Resource**: [Git Tutorial](https://git-scm.com/book/en/v2/Getting-Started-First-Time-Git-Setup)
- **Time**: 1-2 days to learn basics
- **Practice**: Clone a repository and make a change

#### If APIs are new to you:
- **Resource**: [REST API Tutorial](https://restfulapi.net/)
- **Time**: 1 day to understand concepts
- **Practice**: Use Postman to call public APIs

---

## 🚀 Getting Help with Prerequisites

### If You're Stuck

1. **Specific Question**: Ask with what you're confused about
2. **Learning Resources**: We can recommend specific tutorials
3. **Pair Programming**: We can schedule time to work through it together
4. **Simplified Setup**: We can provide a minimal setup guide

### Common Questions

**Q: "I'm not sure if my Python skills are good enough"**
A: If you can understand basic Python syntax and write simple functions, you're ready!

**Q: "I've never worked with APIs before"**
A: No problem! We'll teach you everything you need to know about REST APIs.

**Q: "I'm not comfortable with the command line"**
A: We'll help you get comfortable. Start with basic commands and we'll guide you.

---

## ✅ Prerequisites Checklist

Before starting the project, make sure you can:

- [ ] **Write basic Python functions and classes**
- [ ] **Navigate directories using `cd` and `ls`**
- [ ] **Clone a repository with `git clone`**
- [ ] **Make a simple commit with `git commit`**
- [ ] **Understand basic JSON structure**
- [ ] **Use a code editor (VS Code recommended)**

### If You Can Check All Boxes
**You're ready to start!** Move on to [Quick Setup Guide](04-quick-setup-guide.md).

### If You're Missing Some Items
No problem! Take 1-2 days to review the recommended resources, then come back ready to start.

---

## 🎓 Learning Path

### Week 1: Foundation
- Days 1-2: Python review if needed
- Days 3-4: Git and command line practice
- Day 5: REST API concepts review

### Week 2: Project Setup
- Days 1-2: Environment setup
- Days 3-4: Install all dependencies
- Day 5: First "Hello World" test

**Remember**: Everyone starts somewhere. The goal is to learn and grow!

---

**Questions?** Check the [FAQ](../resources/faq.md) or reach out for help.

**Ready to proceed?** [First 30 Minutes Checklist](03-first-30-minutes.md) →