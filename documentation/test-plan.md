# Test Plan: Open-Instruct Engine

**Audience**: Junior Developers
**Purpose**: Comprehensive testing guide for building reliable educational content generation
**Status**: Planning Phase - Pre-Implementation

---

## Table of Contents
1. [Testing Philosophy](#testing-philosophy)
2. [Test Structure & Organization](#test-structure--organization)
3. [Phase 1: Schema Validation Tests (Test-First)](#phase-1-schema-validation-tests-test-first)
4. [Phase 2: DSPy Module Tests (Mocked)](#phase-2-dspy-module-tests-mocked)
5. [Phase 3: Algorithm Tests (Pure Python)](#phase-3-algorithm-tests-pure-python)
6. [Phase 4: Integration Tests (Test-After)](#phase-4-integration-tests-test-after)
7. [Phase 5: End-to-End Tests](#phase-5-end-to-end-tests)
8. [Test Coverage Goals](#test-coverage-goals)
9. [Continuous Testing Strategy](#continuous-testing-strategy)

---

## Testing Philosophy

### Our Approach: Hybrid TDD

```
┌──────────────────────────────────────────────────────────┐
│ Test-First (Deterministic)                               │
│  ✓ Pydantic Schemas                                      │
│  ✓ Bloom's Taxonomy Validation                           │
│  ✓ Algorithms (prerequisites, sorting)                   │
│  ✓ DSPy Prompts (with mocked LLM responses)              │
└──────────────────────────────────────────────────────────┘
              │
              ▼
┌──────────────────────────────────────────────────────────┐
│ Spike (Prove Technology Works)                          │
│  ✓ Hello World LLM test                                  │
│  ✓ Verify JSON generation capability                     │
└──────────────────────────────────────────────────────────┘
              │
              ▼
┌──────────────────────────────────────────────────────────┐
│ Test-After (Non-Deterministic)                           │
│  ✓ Real LLM Integration Tests                            │
│  ✓ Performance Benchmarks                                │
│  ✓ Golden Dataset Validation                             │
└──────────────────────────────────────────────────────────┘
```

### Why This Approach?

| Test Type | When to Write | Why |
|-----------|--------------|-----|
| **Schema Tests** | **FIRST** | Fast, deterministic, defines "contract" upfront |
| **Mocked Tests** | **FIRST** | Fast feedback (100ms vs 20s), tests logic not LLM |
| **Algorithm Tests** | **FIRST** | Pure Python, easy to test, critical for correctness |
| **Integration Tests** | **AFTER** | Need real LLM outputs first to write assertions |
| **E2E Tests** | **AFTER** | Full system must work before testing end-to-end |

### Red-Green-Refactor Workflow

For **Test-First** components:

1. **RED**: Write a failing test
   ```bash
   pytest tests/test_models.py -k "test_bloom_level_validation" -v
   # Expected: FAILED
   ```

2. **GREEN**: Write minimal code to pass
   ```python
   # src/core/models.py - implement BloomLevel enum
   ```

3. **REFACTOR**: Clean up while keeping tests green
   ```bash
   pytest tests/test_models.py -v
   # Expected: PASSED
   ```

---

## Test Structure & Organization

### Directory Layout

```
backend/
├── tests/
│   ├── __init__.py
│   ├── conftest.py                 # Shared fixtures
│   ├── unit/                       # Fast, isolated tests
│   │   ├── test_models.py          # Pydantic validation
│   │   ├── test_blooms_taxonomy.py # Bloom's verb lists
│   │   ├── test_algorithms.py      # Graph algorithms
│   │   └── test_config.py          # Configuration loading
│   ├── mocked/                     # DSPy with mocked LLM
│   │   ├── test_architect_mocked.py
│   │   ├── test_assessor_mocked.py
│   │   └── test_prerequisites_mocked.py
│   ├── integration/                # Real LLM calls
│   │   ├── test_architect_integration.py
│   │   ├── test_assessor_integration.py
│   │   └── test_dspy_client.py
│   ├── e2e/                        # Full system tests
│   │   ├── test_api_endpoints.py
│   │   └── test_cli.py
│   ├── golden_set.json             # Known good outputs
│   └── benchmarks.py               # Performance tests
```

### pytest Configuration

Create [`pytest.ini`](pytest.ini):
```ini
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts =
    -v
    --strict-markers
    --tb=short
    --cov=src
    --cov-report=html
    --cov-report=term-missing
markers =
    unit: Unit tests (fast, no external dependencies)
    mocked: Mocked LLM tests
    integration: Real LLM calls (slow)
    e2e: End-to-end tests
    slow: Tests that take > 10 seconds
```

### Shared Fixtures ([`tests/conftest.py`](tests/conftest.py))

```python
import pytest
from pydantic import ValidationError
from unittest.mock import Mock, patch

# Sample valid learning objective
@pytest.fixture
def valid_learning_objective():
    return {
        "id": "LO-001",
        "verb": "explain",
        "content": "The difference between lists and tuples in Python",
        "level": "Understand"
    }

# Sample invalid objective (missing required field)
@pytest.fixture
def invalid_learning_objective():
    return {
        "id": "LO-002",
        "verb": "create",
        # Missing: "content"
        "level": "Create"
    }

# Mocked Ollama response
@pytest.fixture
def mock_ollama_response():
    return {
        "model": "deepseek-r1:1.5b",
        "response": '{"topic": "Python Basics", "objectives": [...]}',
        "done": True
    }

# Test topic (consistent across tests)
@pytest.fixture
def sample_topic():
    return "Python functions and decorators"

# Pytest marker for skipping slow tests
def pytest_configure(config):
    config.addinivalue_line(
        "markers", "slow: mark test as slow (deselect with '-m \"not slow\"')"
    )
```

---

## Phase 1: Schema Validation Tests (Test-First)

**Goal**: Define the "contract" for all data structures before writing implementation code.

### Test File: [`tests/unit/test_models.py`](tests/unit/test_models.py)

```python
import pytest
from pydantic import ValidationError
from src.core.models import (
    BloomLevel,
    LearningObjective,
    CourseStructure,
    QuizQuestion
)

class TestBloomLevel:
    """Test Bloom's Taxonomy level enumeration."""

    def test_all_bloom_levels_exist(self):
        """Verify all 6 Bloom levels are defined."""
        expected_levels = {
            "Remember", "Understand", "Apply",
            "Analyze", "Evaluate", "Create"
        }
        actual_levels = {level.value for level in BloomLevel}
        assert actual_levels == expected_levels

    def test_bloom_level_is_enum(self):
        """Bloom levels should be proper enum values."""
        assert BloomLevel.REMEMBER.value == "Remember"
        assert BloomLevel.CREATE.value == "Create"

class TestLearningObjective:
    """Test LearningObjective Pydantic model."""

    def test_valid_learning_objective(self, valid_learning_objective):
        """Should accept valid learning objective."""
        obj = LearningObjective(**valid_learning_objective)
        assert obj.id == "LO-001"
        assert obj.verb == "explain"
        assert obj.level == BloomLevel.UNDERSTAND

    def test_missing_required_field_raises_error(self):
        """Should raise ValidationError if required field is missing."""
        with pytest.raises(ValidationError) as exc_info:
            LearningObjective(
                id="LO-002",
                verb="create",
                # Missing: content
                level=BloomLevel.CREATE
            )
        assert "content" in str(exc_info.value).lower()

    def test_invalid_bloom_level_raises_error(self, valid_learning_objective):
        """Should reject invalid Bloom level."""
        with pytest.raises(ValidationError):
            LearningObjective(
                **valid_learning_objective,
                level="InvalidLevel"  # Not a valid BloomLevel
            )

    def test_verb_must_be_non_empty_string(self, valid_learning_objective):
        """Should reject empty verb."""
        with pytest.raises(ValidationError):
            LearningObjective(
                **valid_learning_objective,
                verb=""
            )

    def test_id_format_lo_prefix(self, valid_learning_objective):
        """Should enforce LO-XXX ID format (optional, can be relaxed)."""
        obj = LearningObjective(**valid_learning_objective)
        assert obj.id.startswith("LO-")

class TestCourseStructure:
    """Test CourseStructure Pydantic model."""

    def test_valid_course_structure(self):
        """Should accept valid course with objectives."""
        course = CourseStructure(
            topic="Python Basics",
            objectives=[
                LearningObjective(
                    id="LO-001",
                    verb="define",
                    content="What a variable is",
                    level=BloomLevel.REMEMBER
                ),
                LearningObjective(
                    id="LO-002",
                    verb="explain",
                    content="Variable naming conventions",
                    level=BloomLevel.UNDERSTAND
                )
            ]
        )
        assert len(course.objectives) == 2
        assert course.topic == "Python Basics"

    def test_empty_objectives_list_is_valid(self):
        """Should accept empty objectives list (edge case)."""
        course = CourseStructure(topic="Empty Topic", objectives=[])
        assert len(course.objectives) == 0

    def test_objectives_must_be_unique_ids(self):
        """Should enforce unique objective IDs."""
        with pytest.raises(ValidationError):
            CourseStructure(
                topic="Python Basics",
                objectives=[
                    LearningObjective(
                        id="LO-001",  # Duplicate ID
                        verb="define",
                        content="First objective",
                        level=BloomLevel.REMEMBER
                    ),
                    LearningObjective(
                        id="LO-001",  # Duplicate ID
                        verb="explain",
                        content="Second objective",
                        level=BloomLevel.UNDERSTAND
                    )
                ]
            )

class TestQuizQuestion:
    """Test QuizQuestion Pydantic model."""

    def test_valid_quiz_question(self):
        """Should accept valid quiz with 4 options."""
        quiz = QuizQuestion(
            stem="What is the output of print(2 + 3)?",
            correct_answer="5",
            distractors=["2", "6", "Error"],
            explanation="In Python, 2 + 3 equals 5"
        )
        assert quiz.stem is not None
        assert len(quiz.distractors) == 3

    def test_exactly_three_distractors_required(self):
        """Should enforce exactly 3 distractors."""
        with pytest.raises(ValidationError):
            QuizQuestion(
                stem="Test question",
                correct_answer="A",
                distractors=["B", "C"],  # Only 2 (should be 3)
                explanation="Test explanation"
            )

    def test_distractors_must_be_unique(self):
        """Should not allow duplicate distractors."""
        with pytest.raises(ValidationError):
            QuizQuestion(
                stem="Test question",
                correct_answer="A",
                distractors=["B", "B", "C"],  # Duplicate "B"
                explanation="Test explanation"
            )

    def test_correct_answer_not_in_distractors(self):
        """Should ensure correct answer is not in distractors."""
        quiz = QuizQuestion(
            stem="Test question",
            correct_answer="A",
            distractors=["B", "C", "D"],
            explanation="Test"
        )
        assert quiz.correct_answer not in quiz.distractors

    def test_all_options_together(self):
        """Helper method should return all 4 options."""
        quiz = QuizQuestion(
            stem="Test",
            correct_answer="A",
            distractors=["B", "C", "D"],
            explanation="Test"
        )
        all_options = quiz.get_all_options()
        assert len(all_options) == 4
        assert "A" in all_options
        assert "B" in all_options
        assert "C" in all_options
        assert "D" in all_options
```

### Implementation Notes for Junior Developers

After writing these tests (which will fail initially), implement [`src/core/models.py`](backend/src/core/models.py):

```python
from enum import Enum
from typing import List
from pydantic import BaseModel, Field, field_validator

class BloomLevel(str, Enum):
    REMEMBER = "Remember"
    UNDERSTAND = "Understand"
    APPLY = "Apply"
    ANALYZE = "Analyze"
    EVALUATE = "Evaluate"
    CREATE = "Create"

class LearningObjective(BaseModel):
    id: str = Field(..., pattern=r"^LO-\d+$")
    verb: str = Field(..., min_length=1)
    content: str = Field(..., min_length=1)
    level: BloomLevel

class CourseStructure(BaseModel):
    topic: str = Field(..., min_length=1)
    objectives: List[LearningObjective] = Field(default_factory=list)

    @field_validator("objectives")
    @classmethod
    def objectives_must_have_unique_ids(cls, v):
        ids = [obj.id for obj in v]
        if len(ids) != len(set(ids)):
            raise ValueError("All objective IDs must be unique")
        return v

class QuizQuestion(BaseModel):
    stem: str = Field(..., min_length=1)
    correct_answer: str = Field(..., min_length=1)
    distractors: List[str] = Field(..., min_length=3, max_length=3)
    explanation: str = Field(..., min_length=1)

    @field_validator("distractors")
    @classmethod
    def distractors_must_be_unique(cls, v):
        if len(v) != len(set(v)):
            raise ValueError("All distractors must be unique")
        return v

    def get_all_options(self) -> List[str]:
        """Return correct answer + distractors as combined list."""
        return [self.correct_answer] + self.distractors
```

---

## Phase 2: DSPy Module Tests (Mocked)

**Goal**: Test DSPy prompt logic without calling Ollama (fast feedback).

### Test File: [`tests/mocked/test_architect_mocked.py`](tests/mocked/test_architect_mocked.py)

```python
import pytest
from unittest.mock import Mock, patch
from src.modules.architect import Architect
from src.core.models import CourseStructure, BloomLevel

class TestArchitectModule:
    """Test the Architect module with mocked Ollama responses."""

    @pytest.fixture
    def architect(self):
        """Initialize Architect module."""
        return Architect()

    @pytest.fixture
    def mock_course_json(self):
        """Mock JSON response from Ollama."""
        return '''{
            "topic": "Python Functions",
            "objectives": [
                {
                    "id": "LO-001",
                    "verb": "define",
                    "content": "What a function is",
                    "level": "Remember"
                },
                {
                    "id": "LO-002",
                    "verb": "explain",
                    "content": "Function parameters",
                    "level": "Understand"
                }
            ]
        }'''

    def test_generate_objectives_with_mocked_llm(
        self,
        architect,
        mock_course_json
    ):
        """Should parse mocked LLM response into CourseStructure."""
        with patch('src.core.dspy_client.lm') as mock_lm:
            # Configure mock to return our JSON
            mock_lm.return_value = Mock(
                response=mock_course_json,
                done=True
            )

            # Call the module
            result = architect.generate(topic="Python Functions")

            # Verify it returns valid CourseStructure
            assert isinstance(result, CourseStructure)
            assert result.topic == "Python Functions"
            assert len(result.objectives) == 2
            assert result.objectives[0].level == BloomLevel.REMEMBER

    def test_architect_handles_invalid_json_gracefully(self, architect):
        """Should raise clear error when LLM returns invalid JSON."""
        with patch('src.core.dspy_client.lm') as mock_lm:
            # Mock returns invalid JSON
            mock_lm.return_value = Mock(
                response="This is not valid JSON {{{",
                done=True
            )

            with pytest.raises(ValueError) as exc_info:
                architect.generate(topic="Python")

            assert "invalid json" in str(exc_info.value).lower()

    def test_architect_retries_on_failure(self, architect):
        """Should retry up to 3 times on JSON parsing failure."""
        with patch('src.core.dspy_client.lm') as mock_lm:
            # First 2 calls fail, 3rd succeeds
            mock_lm.side_effect = [
                Mock(response="invalid", done=True),
                Mock(response="also invalid", done=True),
                Mock(response='{"topic": "Test", "objectives": []}', done=True)
            ]

            result = architect.generate(topic="Test")
            assert isinstance(result, CourseStructure)
            assert mock_lm.call_count == 3

    def test_architect_fails_after_max_retries(self, architect):
        """Should raise error after 3 failed attempts."""
        with patch('src.core.dspy_client.lm') as mock_lm:
            # All calls return invalid JSON
            mock_lm.return_value = Mock(response="invalid", done=True)

            with pytest.raises(ValueError):
                architect.generate(topic="Test")

            assert mock_lm.call_count == 3
```

### Implementation Notes

Junior developers: Notice how we test **error handling** and **edge cases** with mocks:

- **Invalid JSON** - What happens when LLM returns garbage?
- **Retry Logic** - Does it retry the correct number of times?
- **Success Case** - Does it parse valid JSON correctly?

This lets you write robust code **before** connecting to real LLM.

---

## Phase 3: Algorithm Tests (Pure Python)

**Goal**: Test dependency graph and topological sort algorithms (deterministic).

### Test File: [`tests/unit/test_algorithms.py`](tests/unit/test_algorithms.py)

```python
import pytest
from src.modules.algorithms import (
    detect_cycles,
    topological_sort,
    build_dependency_graph
)

class TestCycleDetection:
    """Test circular dependency detection algorithm."""

    def test_no_cycle_returns_empty_list(self):
        """Linear dependencies have no cycles."""
        deps = {
            "LO-001": [],      # No dependencies
            "LO-002": ["LO-001"],  # Depends on 001
            "LO-003": ["LO-002"]   # Depends on 002
        }
        cycles = detect_cycles(deps)
        assert cycles == []

    def test_simple_cycle_detected(self):
        """Detect A → B → A cycle."""
        deps = {
            "LO-001": ["LO-002"],
            "LO-002": ["LO-001"]  # Circular!
        }
        cycles = detect_cycles(deps)
        assert len(cycles) == 1
        assert set(cycles[0]) == {"LO-001", "LO-002"}

    def test_complex_cycle_detected(self):
        """Detect A → B → C → A cycle."""
        deps = {
            "LO-001": ["LO-002"],
            "LO-002": ["LO-003"],
            "LO-003": ["LO-001"]  # Circular!
        }
        cycles = detect_cycles(deps)
        assert len(cycles) == 1
        assert len(cycles[0]) == 3

    def test_multiple_independent_cycles(self):
        """Detect multiple separate cycles."""
        deps = {
            "LO-001": ["LO-002"],
            "LO-002": ["LO-001"],  # Cycle 1
            "LO-003": ["LO-004"],
            "LO-004": ["LO-003"]   # Cycle 2
        }
        cycles = detect_cycles(deps)
        assert len(cycles) == 2

class TestTopologicalSort:
    """Test topological sorting algorithm."""

    def test_linear_dependency_order(self):
        """Should sort in dependency order."""
        deps = {
            "LO-001": [],
            "LO-002": ["LO-001"],
            "LO-003": ["LO-002"]
        }
        sorted_objs = topological_sort(deps)
        assert sorted_objs.index("LO-001") < sorted_objs.index("LO-002")
        assert sorted_objs.index("LO-002") < sorted_objs.index("LO-003")

    def test_parallel_tracks_allowed(self):
        """Independent objectives can be in any order."""
        deps = {
            "LO-001": [],
            "LO-002": [],
            "LO-003": ["LO-001", "LO-002"]
        }
        sorted_objs = topological_sort(deps)
        # LO-003 must come last, but LO-001 and LO-002 can be in any order
        assert sorted_objs[-1] == "LO-003"

    def test_single_objective(self):
        """Single objective with no dependencies."""
        deps = {"LO-001": []}
        sorted_objs = topological_sort(deps)
        assert sorted_objs == ["LO-001"]

class TestDependencyGraph:
    """Test dependency graph construction."""

    def test_build_graph_from_objectives(self):
        """Should construct graph from list of objectives."""
        objectives = [
            {"id": "LO-001", "content": "First"},
            {"id": "LO-002", "content": "Second", "prerequisites": ["LO-001"]}
        ]
        graph = build_dependency_graph(objectives)
        assert "LO-001" in graph
        assert "LO-002" in graph
        assert graph["LO-002"] == ["LO-001"]
```

### Implementation Notes

These algorithms are **critical for correctness**. Test them thoroughly:

- **Happy Path**: Normal dependencies
- **Edge Cases**: Single objective, no dependencies
- **Error Cases**: Cycles, self-dependencies

Junior developers: Implement these **before** integrating with LLM. Use these tests as safety net.

---

## Phase 4: Integration Tests (Test-After)

**Goal**: Test real LLM integration after you know what outputs look like.

### When to Write These Tests

**ONLY AFTER**:
1. Hello World spike succeeds (generates valid JSON at least once)
2. You have 3-5 example outputs to base assertions on
3. Mocked tests all pass

### Test File: [`tests/integration/test_architect_integration.py`](tests/integration/test_architect_integration.py)

```python
import pytest
import time
from src.modules.architect import Architect
from src.core.models import CourseStructure, BloomLevel

@pytest.mark.integration
@pytest.mark.slow
class TestArchitectIntegration:
    """Test real Ollama integration (slow tests!)."""

    @pytest.fixture
    def architect(self):
        """Initialize with real Ollama connection."""
        return Architect()

    def test_generate_real_python_objectives(self, architect):
        """Generate real objectives for 'Python functions'."""
        start = time.time()
        result = architect.generate(
            topic="Python functions and decorators",
            target_audience="Intermediate Python developers"
        )
        duration = time.time() - start

        # Verify structure
        assert isinstance(result, CourseStructure)
        assert len(result.objectives) >= 3  # Should generate at least 3
        assert result.topic == "Python functions and decorators"

        # Verify performance
        assert duration < 30, f"Generation took {duration:.2f}s (too slow!)"

        # Verify Bloom's levels are diverse
        levels = {obj.level for obj in result.objectives}
        assert len(levels) >= 2, "Should use multiple Bloom levels"

    def test_generate_mixed_difficulty_topics(self, architect):
        """Test different difficulty levels."""
        topics = [
            ("Basic arithmetic", "Grade 3 students"),
            ("Calculus derivatives", "College students"),
            ("Quantum entanglement", "Physics PhD students")
        ]

        for topic, audience in topics:
            result = architect.generate(topic=topic, target_audience=audience)
            assert isinstance(result, CourseStructure)
            assert len(result.objectives) > 0

            # Content should be appropriate for audience
            for obj in result.objectives:
                assert obj.content is not None
                assert len(obj.content) > 10  # Not just a few words

    @pytest.mark.skipif(
        "not config.getoption('--run-slow-tests')",
        reason="Too slow for normal test runs"
    )
    def test_json_validity_over_10_runs(self, architect):
        """Test JSON validity rate over 10 consecutive runs."""
        valid_count = 0
        total_runs = 10

        for i in range(total_runs):
            try:
                result = architect.generate(topic=f"Test topic {i}")
                if isinstance(result, CourseStructure):
                    valid_count += 1
            except Exception:
                pass  # Count as invalid

        validity_rate = (valid_count / total_runs) * 100
        print(f"\nJSON Validity Rate: {validity_rate}%")

        assert validity_rate >= 60, \
            f"Validity rate {validity_rate}% below 60% threshold"
```

### Running Integration Tests

```bash
# Run only fast unit tests (default)
pytest

# Run integration tests (slow!)
pytest tests/integration/ -v

# Run only specific integration test
pytest tests/integration/test_architect_integration.py::TestArchitectIntegration::test_generate_real_python_objectives -v -s
```

---

## Phase 5: End-to-End Tests

**Goal**: Test full system from API → LLM → Database.

### Test File: [`tests/e2e/test_api_endpoints.py`](tests/e2e/test_api_endpoints.py)

```python
import pytest
from fastapi.testclient import TestClient
from src.api import app

@pytest.fixture
def client():
    """Test client for FastAPI app."""
    return TestClient(app)

@pytest.mark.e2e
@pytest.mark.slow
class TestAPIEndpoints:
    """Test full API stack."""

    def test_health_endpoint(self, client):
        """Should return 200 and Ollama status."""
        response = client.get("/health")
        assert response.status_code == 200

        data = response.json()
        assert "ollama_connected" in data
        assert "model_version" in data

    def test_generate_objectives_endpoint(self, client):
        """Should generate objectives via POST request."""
        payload = {
            "topic": "REST API design",
            "target_audience": "Backend developers"
        }

        response = client.post("/generate/objectives", json=payload)

        assert response.status_code == 200
        data = response.json()

        assert "topic" in data
        assert "objectives" in data
        assert len(data["objectives"]) >= 3

    def test_generate_quiz_endpoint(self, client):
        """Should generate quiz for specific objective."""
        # First, generate objectives
        objectives_response = client.post(
            "/generate/objectives",
            json={"topic": "Python decorators", "target_audience": "Developers"}
        )
        objectives = objectives_response.json()["objectives"]
        first_objective = objectives[0]

        # Generate quiz for first objective
        quiz_response = client.post(
            "/generate/quiz",
            json={"objective_id": first_objective["id"]}
        )

        assert quiz_response.status_code == 200
        quiz = quiz_response.json()

        assert "stem" in quiz
        assert "correct_answer" in quiz
        assert "distractors" in quiz
        assert len(quiz["distractors"]) == 3

    def test_caching_works(self, client):
        """Second request for same topic should be faster (cached)."""
        import time

        topic = "Database indexing"
        payload = {"topic": topic, "target_audience": "Developers"}

        # First request (uncached)
        start1 = time.time()
        response1 = client.post("/generate/objectives", json=payload)
        duration1 = time.time() - start1

        # Second request (cached)
        start2 = time.time()
        response2 = client.post("/generate/objectives", json=payload)
        duration2 = time.time() - start2

        assert response1.status_code == 200
        assert response2.status_code == 200
        assert duration2 < duration1, "Cached request should be faster"
        assert duration2 < 1.0, "Cached request should be < 1 second"

        # Responses should be identical
        assert response1.json() == response2.json()
```

---

## Test Coverage Goals

### Target Coverage by Module

| Module | Target Coverage | Rationale |
|--------|----------------|-----------|
| `src/core/models.py` | **95%+** | Critical "contract", all edge cases |
| `src/core/dspy_client.py` | **85%+** | LLM client, error handling |
| `src/modules/architect.py` | **90%+** | Core business logic |
| `src/modules/assessor.py` | **90%+** | Quiz generation |
| `src/modules/algorithms.py` | **95%+** | Pure Python, deterministic |
| `src/api.py` | **70%+** | Endpoints covered by E2E tests |

### Generating Coverage Reports

```bash
# Generate HTML coverage report
pytest --cov=src --cov-report=html

# View in browser
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux

# Terminal coverage report
pytest --cov=src --cov-report=term-missing
```

### Coverage CI/CD Gate

Add to [`.github/workflows/test.yml`](.github/workflows/test.yml):
```yaml
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python: '3.11'
      - run: pip install -r requirements.txt
      - run: pytest --cov=src --cov-fail-under=80
```

---

## Continuous Testing Strategy

### Pre-Commit Hooks

Automatically run tests before committing:

```bash
# Install pre-commit
pip install pre-commit

# Create .pre-commit-config.yaml
cat > .pre-commit-config.yaml << 'EOF'
repos:
  - repo: local
    hooks:
      - id: pytest-unit
        name: Run unit tests
        entry: pytest tests/unit/ -v
        language: system
        pass_filenames: false

      - id: pytest-mocked
        name: Run mocked tests
        entry: pytest tests/mocked/ -v
        language: system
        pass_filenames: false

      - id: pytest-coverage
        name: Check coverage
        entry: pytest --cov=src --cov-fail-under=75
        language: system
        pass_filenames: false
EOF

# Install hooks
pre-commit install
```

### Test Workflow for Junior Developers

**Daily Development**:
```bash
# 1. Make changes
vim src/core/models.py

# 2. Run fast tests (unit + mocked)
pytest tests/unit/ tests/mocked/ -v

# 3. Run full test suite (includes slow integration tests)
pytest

# 4. Check coverage
pytest --cov=src --cov-report=term-missing
```

**Before Committing**:
```bash
# Pre-commit hooks automatically run fast tests
git commit -m "Add validation for Bloom's verbs"

# If tests fail, commit is blocked
# Fix issues and try again
```

**Before Pushing**:
```bash
# Run full suite including integration tests
pytest -v

# Verify coverage meets threshold
pytest --cov=src --cov-fail-under=80
```

---

## Troubleshooting Test Failures

### Common Issues & Solutions

| Issue | Cause | Solution |
|-------|-------|----------|
| `ImportError: No module named 'src'` | PYTHONPATH not set | Run `export PYTHONPATH="${PYTHONPATH}:$(pwd)"` |
| Tests timeout after 60s | Ollama not running | Start Ollama: `ollama serve` |
| All LLM tests fail | Model not downloaded | Run: `ollama pull deepseek-r1:1.5b` |
| Mock tests pass but integration fails | Prompt needs tuning | Adjust DSPy prompt, retrain |
| Coverage stuck at 50% | Missing test files | Add tests for uncovered lines |

### Debugging Failed Tests

```bash
# Run with verbose output
pytest tests/unit/test_models.py::TestLearningObjective::test_missing_required_field_raises_error -vv -s

# Drop into debugger on failure
pytest --pdb

# Run last failed tests only
pytest --lf

# Run until first failure
pytest -x
```

---

## Next Steps for Junior Developers

1. **Read this test plan completely** before writing any code
2. **Set up pytest environment** following Test Structure section
3. **Start with Phase 1** (Schema tests) - write tests FIRST
4. **Implement models** to make Phase 1 tests pass
5. **Move to Phase 2** (Mocked tests) - still no real LLM calls
6. **Do Hello World spike** to verify Ollama works
7. **Write Phase 4 tests** based on real LLM outputs
8. **Continuously run** `pytest` while developing

---

## Questions?

If tests fail unexpectedly:
1. Check the troubleshooting table above
2. Review test output carefully: `pytest -vv`
3. Ask senior dev for help (bring test output + error message)

Remember: **Tests are safety nets**. They prevent regressions and document expected behavior.
