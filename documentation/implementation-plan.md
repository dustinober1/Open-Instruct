# Implementation Plan: Open-Instruction Engine

This document outlines the step-by-step plan to build the **Open-Instruction** educational content generation engine. It expands on the `Guiding_Document.md` with specific technical strategies, schemas, and validation methods.

## Core Philosophy
**"Structure over Syntax"**: We prioritize valid, schema-compliant JSON outputs over conversational text. We will leverage **DSPy** for prompt optimization and **Pydantic** for strict validation, with **Ollama** running local models (DeepSeek-R1 1.5B).

---

## Phase 1: Environment & Core Logic Setup
**Goal**: Establish a working local environment where Python can talk to Ollama and specific models.

### Step 1.1: Project Skeleton
*   **Directory Structure**:
    ```text
    open-instruction/
    ├── backend/
    │   ├── src/
    │   │   ├── core/
    │   │   │   ├── config.py       # Settings (Ollama URL, model names)
    │   │   │   ├── dspy_client.py  # DSPy LM configuration
    │   │   │   └── models.py       # Pydantic Schemas (The "Contract")
    │   │   ├── modules/
    │   │   │   ├── architect.py    # Learning Objective Generation
    │   │   │   └── assessor.py     # Quiz Generation
    │   │   └── main.py             # CLI Entry point
    │   ├── requirements.txt
    │   └── .env
    ├── frontend/                   # Next.js app (placeholder for now)
    └── README.md
    ```

### Step 1.2: Dependencies & Configuration
*   **Dependencies**: `dspy-ai`, `pydantic`, `fastapi`, `uvicorn`, `typer` (for CLI).
*   **Configuration**:
    *   Set up `dspy.lm.Ollama` to point to `http://localhost:11434`.
    *   **Crucial**: Configure DSPy to use `deepseek-r1:1.5b`. Since this is a smaller model, we will need to enable `experimental=True` in DSPy if needed, or largely rely on `TypedPredictor` for structured enforcement.

### Step 1.3: The "Contract" (Pydantic Models)
We will strictly define Bloom's Taxonomy in `src/core/models.py`.

```python
from enum import Enum
from pydantic import BaseModel, Field
from typing import List

class BloomLevel(str, Enum):
    REMEMBER = "Remember"
    UNDERSTAND = "Understand"
    APPLY = "Apply"
    ANALYZE = "Analyze"
    EVALUATE = "Evaluate"
    CREATE = "Create"

class LearningObjective(BaseModel):
    id: str = Field(..., description="Unique identifier like 'LO-001'")
    verb: str = Field(..., description="Action verb matching the Bloom level")
    content: str = Field(..., description="The specific learning outcome")
    level: BloomLevel
    
class CourseStructure(BaseModel):
    topic: str
    objectives: List[LearningObjective]
```

---

## Phase 2: The "Brain" (DSPy Modules)
**Goal**: Reliable JSON generation from a 1.5B parameter model.

### Step 2.1: The "Architect" Module (Objectives)
*   **Strategy**: Use `dspy.TypedPredictor` instead of standard `dspy.Predict`.
*   **Signature**:
    ```python
    class GenerateObjectives(dspy.Signature):
        """Generate a list of educational learning objectives based on Bloom's Taxonomy. 
        Output MUST be valid JSON conforming to the CourseStructure schema."""
        
        topic: str = dspy.InputField(desc="The main subject topic")
        target_audience: str = dspy.InputField(desc="The learner persona (e.g., 'Grade 10 students', 'Senior Developers')")
        outcome: CourseStructure = dspy.OutputField(desc="Structured list of objectives")
    ```
*   **Assertions**:
    *   Since 1.5B models can hallucinate formats, we will add `dspy.Assert` to verify that `verb` actually exists in a predefined list of Bloom's verbs for that specific level.

### Step 2.2: The "Assessor" Module (Quizzes)
*   **Distractor Logic**:
    *   The model must generate 1 correct answer and 3 distinct distractors.
    *   **Guardrail**: We will check `len(set(options)) == 4` to ensure no duplicate answers.
*   **Signature**:
    ```python
    class QuizQuestion(BaseModel):
        stem: str = Field(..., description="The question text")
        correct_answer: str
        distractors: List[str] = Field(..., min_length=3, max_length=3)
        explanation: str
    
    class GenerateQuiz(dspy.Signature):
        objective: str = dspy.InputField()
        question: QuizQuestion = dspy.OutputField()
    ```

### Step 2.3: CLI Verification
*   Create `python backend/src/main.py` to run these modules via command line.
*   **Verification**: Run 10 iterations. Success rate > 80% JSON validity required to move to API phase.

---

## Phase 3: The API Layer (FastAPI)
**Goal**: Expose the logic to a frontend.

### Step 3.1: API Setup
*   `GET /health`: Sanity check.
*   `POST /generate/objectives`: Accepts `{ topic: str }`, calls `Architect` module.
*   `POST /generate/quiz`: Accepts `{ objective: str }`, calls `Assessor` module.

### Step 3.2: Async & Error Handling
*   Since local LLMs are slow, these endpoints might take 10-30 seconds.
*   Initial version: Synchronous blocking calls (easiest to debug).
*   Refined version: Background tasks or streaming responses if needed.

---

## Phase 4: The Frontend (Course Builder)
**Goal**: Visual interaction.

### Step 4.1: Next.js + React Flow
*   Initialize `frontend` with Next.js App Router.
*   Install `reactflow` and `shadcn/ui`.

### Step 4.2: Curriculum Graph
*   Map `LearningObjective` nodes to React Flow nodes.
*   Edges represent prerequisite relationships (initially just linear).

### Step 4.3: Editor Panel
*   Clicking a node opens a side sheet to view/edit the generated content.
*   "Regenerate" button calls the API again for that specific node.

---

## Phase 5: Export & Final Polish
### Step 5.1: Export to JSON
*   Button to download the full Pydantic model dump as `course_data.json`.

---

## Phase 6: Testing & Validation Strategy
**Goal**: Ensure reliability before production use.

### Step 6.1: Unit Testing Pyramid
*   **Schema Validation Tests**: Verify Pydantic models catch invalid data (e.g., wrong Bloom levels, duplicate quiz options)
*   **DSPy Module Tests**: Mock LM responses to test prompt logic without calling Ollama
*   **Integration Tests**: Real calls to Ollama with known topics, validate output structure
*   **Target**: 85%+ coverage on core logic

### Step 6.2: LLM Output Quality Metrics
*   **JSON Validity Rate**: Track percentage of valid JSON outputs over 100 runs
*   **Bloom Alignment Score**: Manual spot-check of 20 samples to verify verbs match levels
*   **Distractor Quality**: Ensure quiz distractors are plausible but clearly wrong
*   **Benchmark**: Log average generation time per objective (target: < 15 seconds on local hardware)

### Step 6.3: Golden Dataset
*   Create `tests/golden_set.json` with 10 known topics and their expected outputs
*   Use for regression testing when modifying DSPy prompts

---

## Phase 7: Error Handling & Fallbacks
**Goal**: Graceful degradation when models fail.

### Step 7.1: Retry Logic
*   **Exponential Backoff**: If JSON parsing fails, retry up to 3 times with increased temperature
*   **Prompt Adjustment**: On retry, add stronger formatting instructions to the prompt
*   **Fallback**: After 3 failures, return a structured error with the raw model output for debugging

### Step 7.2: Model Health Checks
*   **Ollama Connectivity Check**: Startup test to verify DeepSeek-R1 is running
*   **Memory Monitoring**: Log system RAM usage during generation (local models can be memory-heavy)
*   **Timeout Protection**: Kill generation after 60 seconds to prevent hangs

### Step 7.3: User-Facing Errors
*   Return clear error messages: "Failed to generate valid JSON after 3 attempts. Try simplifying your topic."
*   Log technical details server-side for debugging

---

## Phase 8: Data Persistence & Caching
**Goal**: Avoid regenerating the same content repeatedly.

### Step 8.1: Simple Storage Layer
*   **SQLite Database**: Store generated courses, objectives, and quizzes
*   **Schema**:
    ```sql
    courses (id, topic, created_at, course_json)
    objectives (id, course_id, bloom_level, content)
    quizzes (id, objective_id, question_json)
    ```
*   **Why SQLite**: Lightweight, no separate server needed, perfect for local-first app

### Step 8.2: LLM Response Caching
*   **Content-Based Caching**: Hash the prompt (topic + target audience) → check DB before calling Ollama
*   **TTL**: Cache for 7 days, then allow regeneration
*   **Benefit**: Instant loading of previously generated courses

### Step 8.3: Export/Import
*   **Full Export**: Download entire database as JSON
*   **Course Import**: Upload previously exported JSON to restore courses
*   **Format**: Versioned JSON schema to handle future model changes

---

## Phase 9: Prerequisite Logic & Curriculum Mapping
**Goal**: Intelligent ordering of learning objectives.

### Step 9.1: Dependency Graph Algorithm
*   **Initial Approach**: Linear progression (Remember → Understand → Apply → ...)
*   **Enhanced Approach**: Use LLM to identify prerequisites:
    ```python
    class IdentifyPrerequisites(dspy.Signature):
        """Identify which objectives are prerequisites for others."""
        objectives: List[str] = dspy.InputField()
        dependencies: Dict[str, List[str]] = dspy.OutputField()
    ```
*   **Output Format**: `{ "LO-003": ["LO-001", "LO-002"] }` meaning LO-003 requires LO-001 and LO-002

### Step 9.2: Cycle Detection
*   **Algorithm**: Detect circular dependencies (e.g., A requires B, B requires A)
*   **Resolution**: Break cycles by removing the lowest-confidence dependency

### Step 9.3: Learning Path Generation
*   **Topological Sort**: Arrange objectives in valid order based on dependencies
*   **Parallel Tracks**: Identify objectives that can be learned simultaneously
*   **Visual Output**: React Flow automatically lays out nodes based on this graph

---

## Phase 10: Performance Optimization
**Goal**: Snappy user experience despite slow local LLMs.

### Step 10.1: Streaming Responses (Optional)
*   Use FastAPI's `StreamingResponse` to send JSON chunks as they're generated
*   Frontend displays progressive loading (e.g., "Generating objectives... 3/5")

### Step 10.2: Parallel Generation
*   Generate quizzes for multiple objectives concurrently using `asyncio.gather()`
*   **Caution**: Monitor RAM usage to avoid OOM on local machines

### Step 10.3: Model Quantization
*   If DeepSeek-R1 1.5B is too slow, explore 4-bit quantized versions
*   Benchmark quality vs. speed tradeoffs

---

## Phase 11: Deployment & Production Readiness
**Goal**: Run reliably for actual users.

### Step 11.1: Docker Containerization
*   **Dockerfile**:
    ```dockerfile
    FROM python:3.11-slim
    # Install Ollama and DeepSeek-R1
    # Copy backend code
    # Expose port 8000
    CMD ["uvicorn", "src.api:app", "--host", "0.0.0.0"]
    ```
*   **Benefit**: Consistent environment, easy deployment

### Step 11.2: Configuration Management
*   Support multiple Ollama models (not just DeepSeek-R1)
*   Allow users to swap models via config file
*   **Validation**: Verify model supports JSON output before use

### Step 11.3: Monitoring
*   **Structured Logging**: JSON logs with timestamps, request IDs, generation times
*   **Metrics Dashboard**: Simple Grafana or custom UI showing:
    - Requests per hour
    - Average generation time
    - Error rate
    - Cache hit rate

---

## Risk Assessment & Mitigation Strategies

### Risk 1: Small Model (1.5B) Cannot Generate Valid JSON Reliably
*   **Probability**: High
*   **Impact**: Blocks entire MVP
*   **Mitigation**:
    1.  Start with "Hello World" test immediately in Session 1
    2.  If JSON validity < 60%, switch to larger model (DeepSeek-R1 7B or Llama 3.2 3B)
    3.  Use `dspy.TypedPredictor` with `max_retries=3` for structured enforcement
    4.  **Fallback**: Use OpenAI API (GPT-4o-mini) for initial development, then optimize for local models

### Risk 2: Local LLM Performance is Too Slow for User Tolerance
*   **Probability**: Medium
*   **Impact**: Poor UX, user abandonment
*   **Mitigation**:
    1.  Set expectations upfront: "Generation takes 15-30 seconds"
    2.  Implement caching immediately (Phase 8) so repeated queries are instant
    3.  Show progress indicators in frontend ("Generating objective 3 of 5...")
    4.  Allow background generation with email/webhook notification when complete

### Risk 3: Bloom's Taxonomy Verb Misalignment
*   **Probability**: Medium
*   **Impact**: Educational quality suffers
*   **Mitigation**:
    1.  Create hardcoded verb lists per level in `src/core/models.py`
    2.  Use DSPy assertions to enforce verbs from approved lists
    3.  Allow user override (manual verb editing in frontend)
    4.  Include "verb justification" field so model explains why it chose that verb

### Risk 4: Ollama Service Unavailable or Crashes
*   **Probability**: Medium (especially during development)
*   **Impact**: System downtime
*   **Mitigation**:
    1.  Health check endpoint (`GET /health`) that pings Ollama
    2.  Auto-restart logic in systemd/supervisor
    3.  User-friendly error: "Ollama service not running. Start it with `ollama serve`"
    4.  Graceful degradation: Show cached courses even if Ollama is down

### Risk 5: Hallucinated Prerequisite Dependencies (Phase 9)
*   **Probability**: High (small models struggle with reasoning)
*   **Impact**: Illogical learning paths
*   **Mitigation**:
    1.  Start with linear Bloom's progression (no dependency detection)
    2.  Add prerequisite detection only after MVP is stable
    3.  Manual override: Users can drag-and-drop to reorder nodes
    4.  Validation: Check if prerequisites create cycles (algorithmic, not LLM-based)

### Risk 6: Frontend Complexity Creep
*   **Probability**: High (React Flow is complex)
*   **Impact**: Delays backend focus
*   **Mitigation**:
    1.  **Phase 1**: CLI-only backend (no frontend)
    2.  **Phase 2**: Simple HTML/JS fetch API (single page, no framework)
    3.  **Phase 3**: Only after backend is proven, add React Flow
    4.  Consider pre-built curriculum visualization libraries

---

## Decision Log

### Decision 1: Why DSPy Instead of Raw LangChain?
*   **Reason**: DSPy's declarative approach separates prompt logic from model calls
*   **Benefit**: Easier to optimize prompts and swap models later
*   **Tradeoff**: Learning curve for team unfamiliar with DSPy

### Decision 2: Why SQLite Instead of PostgreSQL?
*   **Reason**: Local-first app, single user, no need for distributed database
*   **Benefit**: Zero configuration, portable (single file), easy backups
*   **Tradeoff**: Not suitable for multi-user concurrent editing (future problem)

### Decision 3: Why DeepSeek-R1 1.5B Instead of Larger Models?
*   **Reason**: Runs on consumer hardware (8GB RAM), fast inference
*   **Benefit**: True privacy (local only), no API costs
*   **Tradeoff**: May struggle with complex reasoning (mitigated by DSPy assertions)

### Decision 4: Why TypedPredictor Instead of Standard Predict?
*   **Reason**: Forces Pydantic schema compliance at generation time
*   **Benefit**: Higher JSON validity rate, cleaner error handling
*   **Tradeoff**: Slightly slower (DSPy adds validation layer)

---

## Phase 12: Future Enhancements (Post-MVP)
*   **Multi-Model Support**: Allow users to choose between DeepSeek, Llama 3, Mistral, etc.
*   **Fine-Tuning**: Collect user feedback to fine-tune DeepSeek on educational content
*   **Collaborative Editing**: Multiple users editing a course simultaneously
*   **Version History**: Track changes to objectives/quizzes over time
*   **Export Formats**: PDF syllabus, Markdown docs, SCORM packages for LMS integration
*   **AI Tutor**: Chat interface for students to ask questions about generated content

---

## Definition of Done (Acceptance Criteria)

### Phase 1: Environment & Core Logic Setup
**Acceptance Criteria**:
- [ ] Virtual environment created and dependencies installed
- [ ] `src/core/models.py` passes all Pydantic validation tests
- [ ] `src/core/dspy_client.py` successfully connects to Ollama
- [ ] "Hello World" script generates valid JSON for 3 consecutive test topics
- [ ] README.md documents setup instructions (Ollama installation, venv setup)

**Exit Criterion**: Can run `python -m src.modules.architect "Python basics"` and get valid JSON output

---

### Phase 2: The "Brain" (DSPy Modules)
**Acceptance Criteria**:
- [ ] `Architect` module generates 5+ learning objectives per topic
- [ ] All objectives use valid Bloom's Taxonomy verbs from predefined lists
- [ ] `Assessor` module generates quiz questions with exactly 4 unique options
- [ ] CLI runs 10 iterations without crashes
- [ ] JSON validity rate ≥ 80% (8/10 outputs parse successfully)
- [ ] Average generation time ≤ 20 seconds per objective

**Exit Criterion**: Demo script generates a full course outline with objectives and quizzes

---

### Phase 3: The API Layer (FastAPI)
**Acceptance Criteria**:
- [ ] `/health` endpoint returns 200 + Ollama connection status
- [ ] `/generate/objectives` accepts POST request and returns JSON within 30 seconds
- [ ] `/generate/quiz` returns valid quiz question or structured error
- [ ] API documentation accessible at `/docs` (Auto-generated by FastAPI)
- [ ] All endpoints include request IDs for debugging
- [ ] Error responses include actionable messages (not just stack traces)

**Exit Criterion**: Can call API via curl/Postman and generate complete course structure

---

### Phase 4: The Frontend (Course Builder)
**Acceptance Criteria**:
- [ ] Next.js app runs locally (`npm run dev`)
- [ ] Topic input form sends POST request to backend
- [ ] Generated objectives render as nodes in React Flow graph
- [ ] Clicking node opens side panel with objective details
- [ ] "Regenerate" button re-calls API for that specific node
- [ ] Export button downloads `course_data.json`

**Exit Criterion**: End-to-end flow works: Enter topic → See graph → Export course

---

### Phase 5: Export & Final Polish
**Acceptance Criteria**:
- [ ] Downloaded JSON validates against Pydantic schema
- [ ] Export includes metadata (generated_at, model_version, topic)
- [ ] UI shows success notification after export

**Exit Criterion**: User can import exported JSON into another instance and recover full course

---

### Phase 6: Testing & Validation
**Acceptance Criteria**:
- [ ] Unit tests cover all Pydantic models (test invalid inputs)
- [ ] Integration tests cover all API endpoints (mock Ollama responses)
- [ ] Golden dataset includes 10 diverse topics (CS, history, math, languages)
- [ ] Golden dataset tests pass after any prompt changes
- [ ] Code coverage report shows ≥ 85% for `src/core/` and `src/modules/`

**Exit Criterion**: `pytest` passes all tests and generates coverage report

---

### Phase 7: Error Handling & Fallbacks
**Acceptance Criteria**:
- [ ] Ollama timeout triggers retry (max 3 attempts)
- [ ] Invalid JSON triggers re-prompt with stronger constraints
- [ ] All failures log to file with timestamps
- [ ] User sees friendly error message within 5 seconds of failure
- [ ] System recovers automatically when Ollama restarts

**Exit Criterion**: Killing Ollama mid-generation results in graceful error, not crash

---

### Phase 8: Data Persistence & Caching
**Acceptance Criteria**:
- [ ] SQLite database created automatically on first run
- [ ] Generating same topic twice returns cached result (< 1 second)
- [ ] Cache expires after 7 days (configurable)
- [ ] Export/Import preserves all data and relationships
- [ ] Database schema handles version upgrades (add migrations)

**Exit Criterion**: Restart app and previously generated courses still accessible

---

### Phase 9: Prerequisite Logic
**Acceptance Criteria**:
- [ ] LLM identifies at least 1 prerequisite dependency for topics with 5+ objectives
- [ ] Circular dependency detection removes cycles automatically
- [ ] Topological sort produces valid learning order
- [ ] React Flow visualizes prerequisite edges (different style than sequential edges)
- [ ] Manual reordering overrides LLM suggestions

**Exit Criterion**: Complex topic shows non-linear prerequisite graph

---

### Phase 10: Performance Optimization
**Acceptance Criteria**:
- [ ] Parallel quiz generation reduces time by 50% (5 objectives: 10s → 5s)
- [ ] Streaming responses show incremental progress in UI
- [ ] RAM usage stays < 4GB during parallel generation
- [ ] Quantized model (if used) maintains ≥ 75% JSON validity

**Exit Criterion**: 10-objective course generates in < 60 seconds total

---

### Phase 11: Deployment
**Acceptance Criteria**:
- [ ] Docker image builds successfully (`docker build -t open-instruct .`)
- [ ] Container runs with single command (`docker run -p 8000:8000 open-instruct`)
- [ ] Logs include structured JSON for all operations
- [ ] Health check endpoint reports model version and uptime
- [ ] Config file allows swapping models without code changes

**Exit Criterion**: Fresh developer can run app with `docker-compose up` and zero manual setup

---

## Immediate Next Steps (Session 1)

### Task Checklist
1.  **Initialize Project Structure**:
    ```bash
    mkdir -p backend/src/{core,modules} tests logs
    cd backend
    python -m venv venv
    source venv/bin/activate  # or venv\Scripts\activate on Windows
    git init
    echo "venv/" >> .gitignore
    echo "__pycache__/" >> .gitignore
    echo "*.pyc" >> .gitignore
    echo "logs/" >> .gitignore
    ```

2.  **Install Core Dependencies**:
    ```bash
    pip install dspy-ai pydantic fastapi uvicorn typer python-dotenv pytest pytest-coverage
    pip freeze > requirements.txt
    ```

3.  **Verify Ollama Setup**:
    ```bash
    # Ensure Ollama is installed and running
    ollama list  # Should show deepseek-r1:1.5b
    ollama run deepseek-r1:1.5b "Test connection"  # Quick sanity check
    ```

4.  **Implement Core Models** ([`src/core/models.py`](backend/src/core/models.py)):
    - Define `BloomLevel` enum
    - Define `LearningObjective` Pydantic model
    - Define `CourseStructure` Pydantic model
    - Define `QuizQuestion` Pydantic model
    - Add hardcoded Bloom's verb lists per level

5.  **Implement DSPy Client** ([`src/core/dspy_client.py`](backend/src/core/dspy_client.py)):
    - Configure `dspy.lm.Ollama` with `http://localhost:11434`
    - Set model to `deepseek-r1:1.5b`
    - Add simple connection test function

6.  **Create "Hello World" Test** ([`tests/hello_world.py`](tests/hello_world.py)):
    ```python
    # Goal: Generate 2 learning objectives about "Python functions"
    # Verify: Output is valid JSON matching CourseStructure schema
    # Success Criteria: Output parses without Pydantic validation errors
    ```

### Expected Outcomes (End of Session 1)
- ✅ Project skeleton created with all directories
- ✅ All dependencies installed and imported without errors
- ✅ Ollama connection verified
- ✅ Bloom's Taxonomy defined as Python enums/classes
- ✅ DSPy client configured and tested
- ✅ "Hello World" script runs successfully at least once
- ✅ At least one valid JSON output saved to `logs/` for reference

### Red Flags (Stop and Reassess If...)
- ❌ Ollama cannot connect or times out repeatedly
- ❌ DeepSeek-R1 model not available or crashes
- ❌ JSON validity rate = 0% after 5 attempts (try larger model)
- ❌ Pydantic validation errors on all outputs (schema too restrictive?)

### Success Metrics (Before Moving to Phase 2)
- 📊 3/5 "Hello World" runs produce valid JSON (60% validity threshold)
- 📊 Average generation time < 30 seconds
- 📊 No Python import errors or dependency conflicts
