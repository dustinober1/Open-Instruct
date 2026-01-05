# 🎓 Open-Instruct: Educational Content Generation Engine

**Version**: 1.0.0
**Status**: Planning Complete - Ready for Implementation
**Last Updated**: 2025-01-05
**Target Audience**: Junior Developers

---

## 🚀 Welcome to Open-Instruct

This project builds an **AI-powered educational content generation engine** that creates structured learning objectives and quizzes based on Bloom's Taxonomy.

### What You'll Build
- **Course Architecture Module**: Generates learning objectives for any topic
- **Assessment Module**: Creates quizzes with Bloom's Taxonomy alignment
- **REST API**: FastAPI endpoints for content management
- **Multi-LLM Support**: Ollama (local), OpenAI, and Anthropic APIs
- **Caching System**: Optimizes AI response caching
- **Database Layer**: SQLite with persistent storage

### Key Technologies
- **Backend**: Python + FastAPI
- **AI Framework**: DSPy (structured LLM prompting)
- **Database**: SQLite (MVP)
- **LLM Support**: Multiple providers (Ollama, OpenAI, Anthropic)
- **Testing**: pytest + TDD methodology

---

## 🔧 LLM Provider Options

Open-Instruct supports multiple LLM providers, so you can choose what works best for you:

### 🚀 Option 1: Ollama (Recommended - Free & Local)
- **Pros**: No API costs, private, offline capable
- **Models**: DeepSeek-R1 1.5B, Mistral, Llama, etc.
- **Setup**: `ollama pull deepseek-r1:1.5b`
- **Best for**: Privacy, offline use, learning

### 💰 Option 2: OpenAI (Premium - Cloud API)
- **Pros**: High quality, reliable, wide model selection
- **Models**: GPT-4, GPT-3.5-Turbo
- **Setup**: Get API key from openai.com
- **Cost**: Pay-as-you-go (~$0.002-0.06 per 1K tokens)
- **Best for**: Production, highest quality output

### 🧠 Option 3: Anthropic (Premium - Cloud API)
- **Pros**: Constitutional AI, safety-focused
- **Models**: Claude 3, Claude 2.1
- **Setup**: Get API key from anthropic.com
- **Cost**: Pay-as-you-go (~$0.015-0.32 per 1K tokens)
- **Best for**: Safety-critical applications

### 🔗 Provider Comparison

| Provider | Cost | Privacy | Setup Complexity | Quality | Offline |
|----------|------|---------|-----------------|---------|---------|
| **Ollama** | Free | ✅ High | Easy | Good | ✅ Yes |
| **OpenAI** | Paid | ❌ Low | Easy | Excellent | ❌ No |
| **Anthropic** | Paid | ❌ Low | Easy | Very Good | ❌ No |

---

## 🗂️ Document Structure

### Core Planning Documents

| # | Document | Purpose | Read Order |
|---|----------|---------|-----------|
| 1 | [implementation-plan.md](documentation/implementation-plan.md) | Overall project phases & timeline | 1st |
| 2 | [blooms-taxonomy.md](documentation/blooms-taxonomy.md) | Complete verb lists & validation | 2nd |
| 3 | [tdd-workflow.md](documentation/tdd-workflow.md) | Day-to-day development guide | 3rd |

### Technical Specifications

| # | Document | Purpose | Read Order |
|---|----------|---------|-----------|
| 4 | [test-plan.md](documentation/test-plan.md) | Testing strategy & coverage goals | 4th |
| 5 | [dspy-prompt-strategy.md](documentation/dspy-prompt-strategy.md) | Prompt engineering guide | 5th |
| 6 | [api-contract.md](documentation/api-contract.md) | REST API specification | 6th |
| 7 | [database-design.md](documentation/database-design.md) | SQLite database structure | 7th |
| 8 | [error-scenarios.md](documentation/error-scenarios.md) | Error handling & recovery | 8th |

---

## 🎯 Who This Is For

### Primary Audience: Junior Developers
- **You're perfect for this if you:**
  - Know basic Python programming
  - Want to learn AI/LLM integration
  - Are interested in educational technology
  - Want to practice TDD and REST APIs

### What You'll Learn
- DSPy for structured AI prompting
- FastAPI REST API design
- Test-Driven Development (TDD)
- Local LLM integration
- Database design with SQLite
- Error handling and caching strategies

---

## ⏱️ First 30 Minutes Checklist

**Complete this checklist to get oriented:**

- [ ] **Read this README completely** (5 min)
- [ ] **Check prerequisites** below (2 min)
- [ ] **Clone this repository** (1 min)
- [ ] **Read [Project Overview](getting-started/01-project-overview.md)** (5 min)
- [ ] **Read [Prerequisites](getting-started/02-prerequisites.md)** (3 min)
- [ ] **Complete [Quick Setup](getting-started/04-quick-setup-guide.md)** (10 min)
- [ ] **You're ready to start Week 1!** 🎉

---

## 📋 Prerequisites

### Required Knowledge
- **Basic Python**: Variables, functions, classes, basic OOP
- **Git Fundamentals**: Clone, commit, push basics
- **Terminal/CLI**: Command line navigation
- **REST API Concepts**: HTTP methods, JSON responses

### Helpful but Not Required
- **TDD (Test-Driven Development)**: Will teach you
- **FastAPI Web Framework**: Will teach you
- **DSPy AI Framework**: Will teach you
- **SQLite Databases**: Will teach you
- **Ollama**: Local LLM runner (we'll set it up together)

### Tools to Install
```bash
# Python (if not installed)
brew install python  # macOS
# or download from python.org

# Git (if not installed)
brew install git     # macOS
# or download from git-scm.com

# Code Editor (recommended)
# VS Code: https://code.visualstudio.com/
# Install Python extension

# Git Setup
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"
```

### Choose Your LLM Provider

**Option A: Ollama (Recommended - Free)**
```bash
# Install Ollama
brew install ollama  # macOS
# or download from https://ollama.ai/download

# Pull recommended model
ollama pull deepseek-r1:1.5b
```

**Option B: OpenAI API (Paid)**
1. Get API key: https://platform.openai.com/api-keys
2. Add to environment: `OPENAI_API_KEY=your_key_here`

**Option C: Anthropic API (Paid)**
1. Get API key: https://console.anthropic.com/
2. Add to environment: `ANTHROPIC_API_KEY=your_key_here`

---

## 📂 Documentation Structure

### 🚀 Getting Started (Start Here)
| File | Purpose | Time |
|------|---------|------|
| [01-project-overview.md](getting-started/01-project-overview.md) | What this project does and why | 5 min |
| [02-prerequisites.md](getting-started/02-prerequisites.md) | Technical requirements setup | 3 min |
| [03-first-30-minutes.md](getting-started/03-first-30-minutes.md) | Quick orientation guide | 2 min |
| [04-quick-setup-guide.md](getting-started/04-quick-setup-guide.md) | Step-by-step installation | 10 min |

### 📋 Core Documentation (Implementation Guide)
| File | Purpose | Read When |
|------|---------|-----------|
| [implementation-plan.md](documentation/implementation-plan.md) | Project phases & timeline | Week 1, Day 1 |
| [blooms-taxonomy.md](documentation/blooms-taxonomy.md) | Learning objectives framework | Week 1, Day 2 |
| [tdd-workflow.md](documentation/tdd-workflow.md) | Development methodology | Week 1, Day 3 |
| [test-plan.md](documentation/test-plan.md) | Testing strategy | Week 1, Day 4 |
| [dspy-prompt-strategy.md](documentation/dspy-prompt-strategy.md) | AI prompting approach | Week 2, Day 1 |
| [api-contract.md](documentation/api-contract.md) | REST API specification | Week 2, Day 2 |
| [database-design.md](documentation/database-design.md) | Database schema | Week 2, Day 3 |
| [error-scenarios.md](documentation/error-scenarios.md) | Error handling | Week 2, Day 4 |

### 🎯 Practical Examples
| File | Purpose |
|------|---------|
| [api-endpoints.md](examples/api-endpoints.md) | API usage examples |
| [dspy-usage.md](examples/dspy-usage.md) | DSPy code examples |
| [troubleshooting.md](examples/troubleshooting.md) | Common issues & fixes |

### 🔧 Configuration Guides
| File | Purpose |
|------|---------|
| [ollama-setup.md](examples/ollama-setup.md) | Ollama local setup |
| [openai-setup.md](examples/openai-setup.md) | OpenAI API setup |
| [anthropic-setup.md](examples/anthropic-setup.md) | Anthropic API setup |
| [provider-comparison.md](examples/provider-comparison.md) | Choose the right provider |

### 📖 Additional Resources
| File | Purpose |
|------|---------|
| [glossary.md](resources/glossary.md) | Technical terms explained |
| [faq.md](resources/faq.md) | Frequently asked questions |
| [learning-path.md](resources/learning-path.md) | Skill development roadmap |
| [guiding-document.md](resources/guiding-document.md) | Project vision & goals |

---

## 📖 Recommended Reading Order

### For Junior Developers (Starting Implementation)

```
Week 1: Planning & Setup
├─ Day 1: Read documentation/implementation-plan.md
│          Understand project scope & phases
├─ Day 2: Read documentation/blooms-taxonomy.md
│          Understand core domain model
├─ Day 3: Read documentation/tdd-workflow.md
│          Understand development process
└─ Day 4: Read documentation/test-plan.md
	           Understand testing requirements

Week 2: Core Development
├─ Day 1: Choose LLM Provider & Read documentation/dspy-prompt-strategy.md
│          Learn LLM integration
├─ Day 2: Read documentation/api-contract.md
│          Design REST endpoints
├─ Day 3: Read documentation/database-design.md
│          Implement data layer
└─ Day 4: Read documentation/error-scenarios.md
           Implement error handling

Week 3: Multi-LLM Support & Configuration
├─ Day 1: Setup chosen LLM provider
│          Ollama: [ollama-setup.md](examples/ollama-setup.md)
│          OpenAI: [openai-setup.md](examples/openai-setup.md)
│          Anthropic: [anthropic-setup.md](examples/anthropic-setup.md)
├─ Day 2: Read [provider-comparison.md](examples/provider-comparison.md)
│          Learn to switch between providers
├─ Day 3: Implement provider switching logic
└─ Day 4: Test with different providers

Week 4+: Implementation & Refinement
└─ Reference all documents as needed
```

---

## 🎯 Key Concepts by Document

### [implementation-plan.md](documentation/implementation-plan.md)

**Core Concepts**:
- 12 Development Phases
- Risk Assessment (6 major risks)
- Decision Log (4 key decisions)
- Acceptance Criteria for each phase

**Key Takeaways**:
- Start with CLI-only backend (no frontend yet)
- Use Hybrid TDD approach
- Implement caching early (Phase 8)
- Focus on 60% JSON validity threshold

**When to Reference**:
- Planning project timeline
- Understanding phase dependencies
- Checking acceptance criteria
- Mitigating risks

---

### [test-plan.md](documentation/test-plan.md)

**Core Concepts**:
- 5 Testing Phases (Unit → E2E)
- 85%+ Coverage Goal
- Golden Dataset for regression
- Pre-commit hooks

**Key Takeaways**:
- Test-First for schemas & algorithms
- Test-After for LLM integration
- Mock LLM responses for fast tests
- Run tests before every commit

**When to Reference**:
- Writing new tests
- Checking test coverage
- Setting up CI/CD
- Troubleshooting test failures

---

### [tdd-workflow.md](documentation/tdd-workflow.md)

**Core Concepts**:
- Red-Green-Refactor Cycle
- Spike workflow for LLM integration
- Daily development checklist
- Pre-commit procedures

**Key Takeaways**:
- Write failing test FIRST (Red)
- Write minimal code to pass (Green)
- Refactor while tests stay green
- Commit frequently with hooks

**When to Reference**:
- Daily development workflow
- Fixing failing tests
- Determining when to test first vs after
- Pre-commit checklist

---

### [blooms-taxonomy.md](documentation/blooms-taxonomy.md)

**Core Concepts**:
- 6 Cognitive Levels (Remember → Create)
- 180 Approved Verbs (30 per level)
- Verb validation rules
- Level progression requirements

**Key Takeaways**:
- Hardcode verb lists (no LLM choice)
- Validate every verb against level
- Auto-fix invalid verbs
- Progress from simple to complex

**When to Reference**:
- Implementing Pydantic models
- Validating LLM output
- Creating learning objectives
- Fixing verb validation errors

---

### [dspy-prompt-strategy.md](documentation/dspy-prompt-strategy.md)

**Core Concepts**:
- DSPy Signatures & Modules
- TypedPredictor for structured outputs
- Assertion-backed validation
- Prompt optimization workflow

**Key Takeaways**:
- Use TypedPredictor, not raw prompts
- Include schema in instructions
- Add few-shot examples
- Strengthen constraints on retry

**When to Reference**:
- Writing DSPy modules
- Debugging LLM outputs
- Optimizing prompt performance
- Handling invalid JSON

---

### [api-contract.md](documentation/api-contract.md)

**Core Concepts**:
- RESTful endpoints (8 main endpoints)
- JSON request/response formats
- Error codes & handling
- WebSocket events (optional)

**Key Takeaways**:
- All responses have `success` boolean
- Include `meta` with request_id & timing
- Return 503 when Ollama is down
- Use HTTP status codes correctly

**When to Reference**:
- Implementing FastAPI endpoints
- Designing request/response schemas
- Understanding error codes
- Integrating frontend with backend

---

### [database-design.md](documentation/database-design.md)

**Core Concepts**:
- 5 Tables (courses, objectives, quizzes, cache, logs)
- SQLite for MVP
- Foreign key relationships
- Migration strategy with Alembic

**Key Takeaways**:
- Cache LLM responses by prompt hash
- Cascade delete objectives when course deleted
- Log all generation attempts
- Backup database regularly

**When to Reference**:
- Creating database schema
- Writing SQL queries
- Implementing caching layer
- Database optimization

---

### [error-scenarios.md](documentation/error-scenarios.md)

**Core Concepts**:
- 4 Error Categories (Transient, Validation, System, LLM)
- Retry strategies (exponential backoff, jitter)
- Circuit breaker pattern
- Recovery procedures

**Key Takeaways**:
- Retry transient failures (max 3 attempts)
- Never crash silently (always log)
- Return cached results when Ollama down
- Graceful degradation over hard failure

**When to Reference**:
- Implementing error handlers
- Debugging system failures
- Writing recovery procedures
- Understanding error codes

---

## 🚀 Quick Start Guide

### Week 1: Environment Setup (documentation/implementation-plan.md Phase 1)

**Goals**:
- [ ] Create project structure
- [ ] Install dependencies (DSPy, Pydantic, FastAPI)
- [ ] Set up Ollama with DeepSeek-R1 1.5B
- [ ] Write "Hello World" test

**Exit Criterion**: Can generate valid JSON from local LLM

**Reference**: documentation/implementation-plan.md → Immediate Next Steps (Session 1)

---

### Week 2: Core Models & Tests (documentation/blooms-taxonomy.md)

**Goals**:
- [ ] Implement `BloomLevel` enum
- [ ] Implement `LearningObjective` Pydantic model
- [ ] Implement `CourseStructure` Pydantic model
- [ ] Add 180 approved verbs
- [ ] Write unit tests (Test-First!)

**Exit Criterion**: All Pydantic models pass validation tests

**Reference**: documentation/blooms-taxonomy.md → Implementation Specification

---

### Week 3: DSPy Integration (documentation/dspy-prompt-strategy.md)

**Goals**:
- [ ] Implement `Architect` module (objectives)
- [ ] Implement `Assessor` module (quizzes)
- [ ] Add verb validation assertions
- [ ] Achieve 60%+ JSON validity rate

**Exit Criterion**: CLI generates valid course structure

**Reference**: documentation/dspy-prompt-strategy.md → Complete Prompt Templates

---

### Week 4: REST API (documentation/api-contract.md)

**Goals**:
- [ ] Implement FastAPI endpoints
- [ ] Add request/response validation
- [ ] Implement caching layer
- [ ] Add error handlers

**Exit Criterion**: Can call API via Postman/curl

**Reference**: documentation/api-contract.md → Endpoints

---

### Week 5: Database & Persistence (documentation/database-design.md)

**Goals**:
- [ ] Create SQLite database schema
- [ ] Implement CRUD operations
- [ ] Add caching by prompt hash
- [ ] Set up automated backups

**Exit Criterion**: Can save and retrieve courses

**Reference**: documentation/database-design.md → Queries

---

### Week 6: Error Handling & Polish (documentation/error-scenarios.md)

**Goals**:
- [ ] Add retry logic with exponential backoff
- [ ] Implement circuit breaker pattern
- [ ] Add structured logging
- [ ] Create error recovery procedures

**Exit Criterion**: System handles failures gracefully

**Reference**: documentation/error-scenarios.md → Recovery Procedures

---

## 📋 Checklists

### Pre-Implementation Checklist

- [ ] Read all 8 documentation documents
- [ ] Install Ollama and DeepSeek-R1 1.5B
- [ ] Verify Ollama connectivity (`ollama list`)
- [ ] Create project directory structure
- [ ] Set up virtual environment
- [ ] Install all dependencies
- [ ] Run "Hello World" spike test
- [ ] Achieve 60%+ JSON validity rate

### Pre-Commit Checklist

- [ ] All unit tests pass (`pytest tests/unit/ tests/mocked/`)
- [ ] Code coverage ≥ 75% (`pytest --cov=src`)
- [ ] No import errors
- [ ] Linting passes (if configured)
- [ ] Documentation updated (if needed)

### Pre-Push Checklist

- [ ] Full test suite passes (including integration tests)
- [ ] Manual testing completed
- [ ] Error scenarios tested
- [ ] Database migrations applied
- [ ] Performance benchmarks acceptable

---

## 🔗 Cross-References

### How Documents Relate

```
documentation/implementation-plan.md (Master Plan)
    │
    ├─► documentation/test-plan.md (How to test each phase)
    │
    ├─► documentation/blooms-taxonomy.md (Core domain model)
    │       │
    │       ├─► documentation/dspy-prompt-strategy.md (How to prompt LLM)
    │       │       │
    │       │       └─► documentation/error-scenarios.md (When prompting fails)
    │       │
    │       └─► documentation/database-design.md (Store objectives)
    │
    ├─► documentation/api-contract.md (Expose functionality)
    │       │
    │       └─► documentation/error-scenarios.md (API error responses)
    │
    └─► documentation/tdd-workflow.md (How to develop day-to-day)
            │
            └─► documentation/test-plan.md (Testing execution)
```

### Common Workflows

**Workflow 1: Adding New Feature**
1. Check **documentation/implementation-plan.md** for phase requirements
2. Follow **documentation/tdd-workflow.md** (Red-Green-Refactor)
3. Write tests per **documentation/test-plan.md**
4. Handle errors per **documentation/error-scenarios.md**
5. Update **documentation/api-contract.md** if adding endpoint

**Workflow 2: Debugging LLM Issue**
1. Check **documentation/dspy-prompt-strategy.md** for prompt templates
2. Review **documentation/error-scenarios.md** for common failures
3. Check logs (structured logging)
4. Adjust prompt and retry
5. Document fix in **documentation/test-plan.md** golden dataset

**Workflow 3: Database Migration**
1. Review **documentation/database-design.md** for schema
2. Create Alembic migration
3. Test migration on backup
4. Apply migration
5. Update **documentation/api-contract.md** if schema changed

---

## 📞 Getting Help

### Questions About Implementation

1. **First**: Check the relevant documentation
2. **Second**: Search codebase for similar patterns
3. **Third**: Ask senior developer with:
   - What you've tried
   - Expected vs actual behavior
   - Error messages/logs
   - Document section you're following

### 💡 What to Do When Stuck

### Common Issues & Quick Fixes

| Issue | Solution | Reference |
|-------|----------|-----------|
| **Ollama connection error** | Check Ollama is running: `ollama list` | error-scenarios.md#scenario-1 |
| **Invalid JSON from LLM** | Check DSPy prompt templates, add examples | dspy-prompt-strategy.md#common-failures |
| **Wrong Bloom's verbs** | Validate against hardcoded verb lists | blooms-taxonomy.md#validation |
| **Test failures** | Run tests with `-v` flag, check TDD workflow | tdd-workflow.md#troubleshooting |
| **API 500 errors** | Check logs, implement error handlers | error-scenarios.md#error-responses |

### Getting Help Process

1. **Check Documentation First**
   - Look at relevant sections in this README
   - Check specific document "When to Reference" sections
   - Review troubleshooting examples

2. **Search Codebase**
   ```bash
   # Search for similar patterns
   grep -r "your-error-pattern" src/
   ```

3. **Ask for Help With:**
   - What you've tried (3+ attempts)
   - Expected vs actual behavior
   - Error messages/logs
   - Document section you're following

4. **Before Asking:**
   - Search existing issues
   - Check troubleshooting.md
   - Run tests and verify setup

---

## 📊 Success Metrics

### Per-Phase Metrics (from documentation/implementation-plan.md)

**Phase 1**: Environment Setup
- [ ] Project structure created
- [ ] Dependencies installed
- [ ] Ollama connection verified
- [ ] Hello World generates valid JSON (60%+ validity)

**Phase 2**: DSPy Modules
- [ ] Generates 5+ objectives per topic
- [ ] All verbs match Bloom's level
- [ ] JSON validity ≥ 80%
- [ ] Generation time < 20s per objective

**Phase 3**: API Layer
- [ ] All endpoints return 200 on success
- [ ] Error responses are clear and actionable
- [ ] Request IDs included for debugging

**Phase 4-5**: Frontend & Polish
- [ ] End-to-end flow works
- [ ] Export/import functional
- [ ] User can build complete course

---

## 🔄 Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2025-01-05 | Initial documentation set (8 documents) |
| - | - | Future versions will track updates |

---

## 🎓 Learning Path for Junior Developers

### Month 1: Read & Understand
- **Week 1**: Read all documents lightly
- **Week 2**: Re-read while setting up environment
- **Week 3**: Reference during initial implementation
- **Week 4**: Deep dive into specific sections as needed

### Month 2: Practice & Apply
- Follow TDD workflow daily
- Refer to documentation/api-contract.md when building endpoints
- Use documentation/error-scenarios.md when debugging
- Check documentation/test-plan.md for coverage requirements

### Month 3: Master & Optimize
- Optimize prompts using DSPy guide
- Refine error handling strategies
- Improve test coverage
- Contribute back to documentation

---

## 📝 Documentation Maintenance

### When to Update Docs

- **After architectural changes**: Update `documentation/implementation-plan.md`
- **After API changes**: Update `documentation/api-contract.md`
- **After schema changes**: Update `documentation/database-design.md`
- **After bug fixes**: Update `documentation/error-scenarios.md`
- ** quarterly**: Review and update all documents

### How to Update

1. Discuss with team
2. Make changes to relevant document
3. Update version number
4. Add entry to Version History table
5. Commit with clear message: `docs: Updated documentation/api-contract.md with new endpoints`

---

## 🎯 Quick Reference Commands

```bash
# Project setup
mkdir -p backend/src/{api,core,modules} backend/{tests,logs,data}
cd backend && python3 -m venv venv
source venv/bin/activate
pip install dspy-ai pydantic fastapi uvicorn typer python-dotenv pytest pytest-cov

# Ollama setup
ollama pull deepseek-r1:1.5b
ollama list

# Run tests
pytest tests/unit/ tests/mocked/ -v

# Run with coverage
pytest --cov=src --cov-report=html

# Start API server
uvicorn src.api.main:app --reload

# Check database
sqlite3 data/open_instruct.db ".tables"
sqlite3 data/open_instruct.db "SELECT COUNT(*) FROM courses;"

# View logs
tail -f logs/production.log
```

---

## 🌟 Success Criteria

**Documentation is successful if**:
- ✅ Junior developers can implement without constant supervision
- ✅ All questions have answers in documentation
- ✅ Code examples are copy-pasteable
- ✅ Edge cases are documented
- ✅ Recovery procedures are clear

---

**Remember**: These documents are **living guides**. Update them as you learn, discover patterns, and improve the system. Your contributions make the next junior developer's journey smoother!

---

## 📧 Document Feedback

Found an error? Something unclear? Missing information?

**Document your feedback** in the project issues:
1. Which document needs updating
2. Which section is unclear
3. What information is missing
4. Suggested improvement

**Pull requests welcome!** Help us make these documents better for everyone.

---

**Last Updated**: 2025-01-05
**Maintained By**: Development Team
**Status**: ✅ Planning Complete - Ready for Implementation
