# 🚀 Project Overview: Open-Instruct

**Version**: 1.0.0
**Last Updated**: 2025-01-05

---

## 🎯 What is Open-Instruct?

Open-Instruct is an **AI-powered educational content generation engine** that automatically creates structured learning objectives and assessment questions based on Bloom's Taxonomy.

### The Vision
We're building a system that helps educators:
- Generate comprehensive learning objectives for any subject
- Create aligned quiz questions with proper cognitive level assessment
- Save hours of lesson planning time
- Ensure educational content follows proven learning frameworks

### How It Works

```mermaid
graph LR
    A[User Input] --> B[Topic & Difficulty]
    B --> C[Architect Module]
    C --> D[Bloom's Objectives]
    D --> E[Assessor Module]
    E --> F[Quiz Questions]
    F --> G[JSON Output]
    G --> H[Database Storage]
    H --> I[REST API]
    I --> J[Educational Platform]
```

### Core Components

1. **Course Architecture Module**
   - Takes topic input (e.g., "Introduction to Python")
   - Generates 5-7 learning objectives using Bloom's Taxonomy
   - Validates verbs against approved list
   - Outputs structured JSON

2. **Assessment Module**
   - Creates quiz questions for each objective
   - Ensures question complexity matches objective level
   - Generates multiple choice, short answer, essay questions
   - Validates question quality

3. **REST API Layer**
   - FastAPI endpoints for content generation
   - Request/response validation
   - Error handling and caching
   - Documentation with OpenAPI

4. **Local LLM Integration**
   - Uses DeepSeek-R1 1.5B via Ollama
   - DSPy for structured prompting
   - Caches responses for performance
   - Fallback when LLM unavailable

5. **Database Layer**
   - SQLite for persistence
   - Cache LLM responses by prompt hash
   - Track generation attempts and success rates
   - Backup and migration support

## 🎓 Why Bloom's Taxonomy?

Bloom's Taxonomy provides a proven framework for:
- **Cognitive Level Progression**: From Remember → Understand → Apply → Analyze → Evaluate → Create
- **Verb Alignment**: Each level has specific action verbs
- **Learning Objectives**: Clear, measurable goals
- **Assessment Design**: Questions that match objective complexity

### The 6 Cognitive Levels

| Level | Verbs | Example Objective |
|-------|-------|-------------------|
| **Remember** | identify, list, define, name | *List the three branches of government* |
| **Understand** | explain, describe, summarize, discuss | *Explain the process of photosynthesis* |
| **Apply** | implement, execute, use, demonstrate | *Use the quadratic formula to solve equations* |
| **Analyze** | compare, contrast, examine, classify | *Compare and contrast democracy and communism* |
| **Evaluate** | judge, critique, assess, recommend | *Critique the effectiveness of this marketing campaign* |
| **Create** | design, build, develop, formulate | *Design a sustainable city plan* |

## 🎯 Key Features

### For Educators
- **Generate Objectives**: 5-7 Bloom's Taxonomy-aligned objectives per topic
- **Create Assessments**: Auto-generate quiz questions by cognitive level
- **Export Options**: JSON, CSV, or API integration
- **Customizable**: Adjust difficulty, subject, grade level

### For Developers
- **Local AI**: No API costs, runs on your machine
- **Structured Output**: Guaranteed JSON format with validation
- **TDD Approach**: Test-driven development throughout
- **Modular Design**: Easy to extend and maintain
- **Performance**: Caching for fast repeated generations

## 🛠️ Technical Stack

- **Language**: Python 3.9+
- **AI Framework**: DSPy (structured LLM prompting)
- **Web Framework**: FastAPI (async, auto-docs)
- **Database**: SQLite (MVP)
- **LLM**: DeepSeek-R1 1.5B via Ollama
- **Testing**: pytest with TDD methodology
- **Validation**: Pydantic models
- **Caching**: Response caching by prompt hash

## 🚀 Success Criteria

### Phase 1 ✅ (Complete)
- [ ] Project structure created
- [ ] Dependencies installed
- [ ] Ollama connection verified
- [ ] "Hello World" test passes

### Phase 2 ✅ (In Progress)
- [ ] Generate 5+ objectives per topic
- [ ] All verbs match Bloom's level
- [ ] JSON validity ≥ 80%
- [ ] Generation time < 20s per objective

### Phase 3 📋 (Next)
- [ ] All endpoints return 200 on success
- [ ] Error responses are clear
- [ ] Request IDs included for debugging

### Phase 4 📋 (Later)
- [ ] SQLite schema created
- [ ] CRUD operations work
- [ ] Caching functional

### Phase 5 📋 (Final)
- [ ] Retry logic implemented
- [ ] Circuit breaker pattern
- [ ] Graceful degradation

## 🎯 Learning Objectives for This Project

As a junior developer, you'll learn:

### Technical Skills
- **DSPy Integration**: Structured AI prompting
- **FastAPI**: Modern web API development
- **SQLite**: Database design and operations
- **TDD**: Test-driven development practices
- **Error Handling**: Robust error management
- **Caching**: Performance optimization

### Soft Skills
- **Problem Solving**: Debugging LLM outputs
- **Code Quality**: Clean, maintainable code
- **Documentation**: Writing clear technical docs
- **Project Management**: Following structured phases

## 🔗 How to Use This Project

### For Educators
1. Use the generated objectives for lesson planning
2. Create assessments aligned with cognitive levels
3. Export content for your Learning Management System
4. Customize objectives for your specific needs

### For Developers
1. Follow the implementation plan week by week
2. Use TDD practices throughout development
3. Reference the DSPy guide for AI integration
4. Extend the system as needed

## 🎓 Next Steps

1. **Read [Prerequisites](02-prerequisites.md)** to ensure you're ready
2. **Follow [Quick Setup](04-quick-setup-guide.md)** to get your environment ready
3. **Start with [Implementation Plan](../documentation/implementation-plan.md)** Week 1, Day 1

---

**Questions?** Check the [FAQ](../resources/faq.md) or reach out to the development team.

**Ready to start?** Complete the [First 30 Minutes Checklist](03-first-30-minutes.md)!