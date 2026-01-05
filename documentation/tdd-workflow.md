# TDD Workflow: Day-to-Day Development Guide

**Audience**: Junior Developers
**Purpose**: Step-by-step guide for Test-Driven Development on Open-Instruct
**Prerequisite**: Read [Test_Plan.md](Test_Plan.md) first

---

## Table of Contents
1. [Daily Development Workflow](#daily-development-workflow)
2. [The Red-Green-Refactor Cycle](#the-red-green-refactor-cycle)
3. [Phase 1: Test-First Workflow (Schemas & Algorithms)](#phase-1-test-first-workflow-schemas--algorithms)
4. [Phase 2: Spike Workflow (LLM Integration)](#phase-2-spike-workflow-llm-integration)
5. [Phase 3: Test-After Workflow (Integration Tests)](#phase-3-test-after-workflow-integration-tests)
6. [Common TDD Mistakes to Avoid](#common-tdd-mistakes-to-avoid)
7. [Troubleshooting When Tests Won't Pass](#troubleshooting-when-tests-wont-pass)
8. [Checklist Before Committing](#checklist-before-committing)

---

## Daily Development Workflow

### Morning Setup (5 minutes)

```bash
# 1. Pull latest changes
cd /path/to/Open_Instruct/backend
git pull origin main

# 2. Activate virtual environment
source venv/bin/activate  # or venv\Scripts\activate on Windows

# 3. Verify Ollama is running
ollama list
# Should show: deepseek-r1:1.5b

# 4. Run full test suite (ensure nothing broke)
pytest -v

# 5. Check coverage
pytest --cov=src --cov-report=term-missing
```

### Choosing What to Work On

Use this decision tree:

```
Start
 │
 ├─ Are you implementing NEW Pydantic model?
 │   └─→ YES: Use Phase 1 (Test-First)
 │
 ├─ Are you implementing NEW algorithm?
 │   └─→ YES: Use Phase 1 (Test-First)
 │
 ├─ Are you modifying DSPy prompt?
 │   └─→ YES: Use Phase 1 (Test-First with mocks)
 │
 ├─ Are you integrating with LLM for first time?
 │   └─→ YES: Use Phase 2 (Spike)
 │
 └─ Are you adding integration test for EXISTING code?
     └─→ YES: Use Phase 3 (Test-After)
```

---

## The Red-Green-Refactor Cycle

### Visual Workflow

```
┌──────────────────────────────────────────────────────┐
│ 1. RED: Write failing test                          │
│    - Run test: FAILED ✗                            │
│    - Duration: 2-10 minutes                         │
└──────────────────────────────────────────────────────┘
                    ↓
┌──────────────────────────────────────────────────────┐
│ 2. GREEN: Write minimal code to pass                │
│    - Run test: PASSED ✓                             │
│    - Duration: 5-30 minutes                         │
│    - Rule: Write ONLY enough code to pass           │
└──────────────────────────────────────────────────────┘
                    ↓
┌──────────────────────────────────────────────────────┐
│ 3. REFACTOR: Clean up while tests stay green       │
│    - Run test: STILL PASSED ✓                       │
│    - Duration: 5-15 minutes                         │
│    - Rule: Improve code without changing behavior   │
└──────────────────────────────────────────────────────┘
                    ↓
               Repeat
```

### Example: Adding Bloom's Verb Validation

#### Step 1: RED (Write Failing Test)

```bash
# Create test file
vim tests/unit/test_blooms_taxonomy.py
```

```python
# tests/unit/test_blooms_taxonomy.py
import pytest
from src.core.models import validate_bloom_verb

class TestBloomVerbValidation:
    def test_valid_verb_for_remember_level(self):
        """'Define' should be valid for Remember level."""
        assert validate_bloom_verb("define", "Remember") == True

    def test_invalid_verb_for_remember_level(self):
        """'Evaluate' should NOT be valid for Remember level."""
        assert validate_bloom_verb("evaluate", "Remember") == False
```

```bash
# Run test - it should FAIL (function doesn't exist yet)
pytest tests/unit/test_blooms_taxonomy.py -v

# Expected output:
# FAILED - ImportError: cannot import name 'validate_bloom_verb'
```

#### Step 2: GREEN (Write Minimal Code)

```bash
# Implement the function
vim src/core/models.py
```

```python
# src/core/models.py
BLOOMS_VERBS = {
    "Remember": ["define", "list", "name", "identify"],
    "Understand": ["explain", "describe", "summarize", "interpret"],
    "Apply": ["apply", "implement", "execute", "use"],
    "Analyze": ["analyze", "differentiate", "distinguish", "examine"],
    "Evaluate": ["evaluate", "assess", "judge", "critique"],
    "Create": ["create", "design", "construct", "formulate"]
}

def validate_bloom_verb(verb: str, level: str) -> bool:
    """Check if verb is valid for given Bloom's level."""
    return verb in BLOOMS_VERBS.get(level, [])
```

```bash
# Run test again - should PASS
pytest tests/unit/test_blooms_taxonomy.py -v

# Expected output:
# PASSED ✓
```

#### Step 3: REFACTOR (Improve Code)

```python
# src/core/models.py (refactored)
from enum import Enum
from typing import Dict, List

class BloomLevel(str, Enum):
    REMEMBER = "Remember"
    UNDERSTAND = "Under"
    APPLY = "Apply"
    # ... etc

class BloomsTaxonomy:
    """Encapsulate Bloom's Taxonomy logic."""

    VERBS: Dict[str, List[str]] = {
        "Remember": ["define", "list", "name", "identify"],
        "Understand": ["explain", "describe", "summarize", "interpret"],
        # ... etc
    }

    @classmethod
    def validate_verb(cls, verb: str, level: str) -> bool:
        """Check if verb is valid for given Bloom's level."""
        return verb.lower() in [v.lower() for v in cls.VERBS.get(level, [])]

# Keep backward compatibility
def validate_bloom_verb(verb: str, level: str) -> bool:
    return BloomsTaxonomy.validate_verb(verb, level)
```

```bash
# Verify tests still pass after refactoring
pytest tests/unit/test_blooms_taxonomy.py -v

# Expected output:
# PASSED ✓
```

---

## Phase 1: Test-First Workflow (Schemas & Algorithms)

**Use for**: Pydantic models, algorithms, DSPy prompts (with mocks)

### Step-by-Step Process

#### 1. Understand Requirements

Before writing tests, ask:
- What input will this receive?
- What output should it produce?
- What edge cases exist?
- What errors should it raise?

**Example**: Implementing `QuizQuestion` model

**Requirements**:
- Input: `stem`, `correct_answer`, `distractors` (list of 3), `explanation`
- Validation: Exactly 3 distractors, all unique
- Output: Validated Pydantic model

#### 2. Write Test Cases (RED)

```bash
# Create test file
vim tests/unit/test_models.py
```

```python
import pytest
from pydantic import ValidationError
from src.core.models import QuizQuestion

class TestQuizQuestion:
    def test_valid_quiz_question(self):
        """Accept valid quiz with 4 options."""
        quiz = QuizQuestion(
            stem="What is 2 + 2?",
            correct_answer="4",
            distractors=["3", "5", "6"],
            explanation="Basic arithmetic"
        )
        assert quiz.stem == "What is 2 + 2?"

    def test_exactly_three_distractors_required(self):
        """Reject if not exactly 3 distractors."""
        with pytest.raises(ValidationError):
            QuizQuestion(
                stem="Test",
                correct_answer="A",
                distractors=["B", "C"],  # Only 2
                explanation="Test"
            )

    def test_distractors_must_be_unique(self):
        """Reject duplicate distractors."""
        with pytest.raises(ValidationError):
            QuizQuestion(
                stem="Test",
                correct_answer="A",
                distractors=["B", "B", "C"],  # Duplicate
                explanation="Test"
            )
```

```bash
# Run tests - expect FAILURE
pytest tests/unit/test_models.py::TestQuizQuestion -v

# Output: FAILED - QuizQuestion doesn't exist yet
```

#### 3. Implement Model (GREEN)

```bash
# Create implementation
vim src/core/models.py
```

```python
from pydantic import BaseModel, Field, field_validator
from typing import List

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
```

```bash
# Run tests - expect PASS
pytest tests/unit/test_models.py::TestQuizQuestion -v

# Output: PASSED ✓
```

#### 4. Add More Tests (Edge Cases)

Think about:
- Empty strings
- Very long strings
- Special characters
- None values
- Wrong data types

```python
def test_empty_stem_raises_error(self):
    """Reject empty question stem."""
    with pytest.raises(ValidationError):
        QuizQuestion(
            stem="",  # Empty!
            correct_answer="A",
            distractors=["B", "C", "D"],
            explanation="Test"
        )
```

#### 5. Refactor (If Needed)

Ask:
- Is code DRY (Don't Repeat Yourself)?
- Are validations in the right place?
- Should logic be extracted to separate function?

---

## Phase 2: Spike Workflow (LLM Integration)

**Use for**: First-time LLM integration, proving technology works

### What is a Spike?

A **spike** is a time-boxed investigation to answer a technical question. It's NOT TDD - it's research.

**Example Questions**:
- Can DeepSeek-R1 1.5B generate valid JSON?
- What's the average generation time?
- What do real outputs look like?

### Spike Workflow

```
1. Define Question (5 min)
   ↓
2. Write Quick Prototype (30-60 min)
   ↓
3. Run Experiment (10-30 min)
   ↓
4. Document Findings (10 min)
   ↓
5. Decide Next Steps
```

### Example Spike: Can DeepSeek Generate Valid JSON?

#### Step 1: Define Question

**Question**: Can DeepSeek-R1 1.5b generate valid JSON matching our `CourseStructure` schema?

**Success Criteria**:
- 3/5 attempts produce valid JSON (60% validity rate)
- Generation time < 30 seconds per attempt
- Output matches Pydantic schema

#### Step 2: Write Prototype

```bash
# Create spike script
vim tests/spikes/hello_world.py
```

```python
#!/usr/bin/env python3
"""
Spike: Test if DeepSeek-R1 can generate valid JSON.
This is NOT a test - it's an experiment.
"""

import dspy
import json
from pathlib import Path
from src.core.models import CourseStructure

# Configure DSPy with Ollama
lm = dspy.lm.Ollama(model="deepseek-r1:1.5b")
dspy.settings.configure(lm=lm)

def test_json_generation(topic: str, run_number: int):
    """Try to generate learning objectives for a topic."""
    print(f"\n{'='*60}")
    print(f"Run #{run_number}: Generating objectives for '{topic}'")
    print(f"{'='*60}")

    prompt = f"""
    Generate a JSON response with learning objectives for: {topic}

    Format:
    {{
        "topic": "{topic}",
        "objectives": [
            {{
                "id": "LO-001",
                "verb": "define",
                "content": "What {topic} is",
                "level": "Remember"
            }}
        ]
    }}

    Return ONLY valid JSON. No additional text.
    """

    try:
        # Call LLM
        response = lm(prompt)
        raw_output = response.response

        print(f"Raw LLM Output:\n{raw_output}\n")

        # Try to parse JSON
        parsed = json.loads(raw_output)

        # Try to validate with Pydantic
        course = CourseStructure(**parsed)

        print(f"✅ SUCCESS: Valid JSON generated!")
        print(f"   Topic: {course.topic}")
        print(f"   Objectives: {len(course.objectives)}")

        # Save successful output
        output_dir = Path("logs/spikes")
        output_dir.mkdir(parents=True, exist_ok=True)

        output_file = output_dir / f"run_{run_number}_success.json"
        with open(output_file, "w") as f:
            json.dump(parsed, f, indent=2)

        print(f"   Saved to: {output_file}")
        return True

    except json.JSONDecodeError as e:
        print(f"❌ FAILED: Invalid JSON")
        print(f"   Error: {e}")
        return False

    except Exception as e:
        print(f"❌ FAILED: Validation error")
        print(f"   Error: {e}")
        return False

if __name__ == "__main__":
    topics = [
        "Python functions",
        "Machine learning basics",
        "React hooks",
        "SQL databases",
        "Git version control"
    ]

    results = []
    for i, topic in enumerate(topics, 1):
        success = test_json_generation(topic, i)
        results.append(success)

    # Summary
    print(f"\n{'='*60}")
    print("SPIKE RESULTS SUMMARY")
    print(f"{'='*60}")
    success_count = sum(results)
    validity_rate = (success_count / len(results)) * 100
    print(f"Valid JSON: {success_count}/{len(results)}")
    print(f"Validity Rate: {validity_rate:.1f}%")

    if validity_rate >= 60:
        print("\n✅ SPIKE PASSED: Model can generate valid JSON")
        print("   → Proceed with Test-First development")
    else:
        print("\n❌ SPIKE FAILED: Model cannot reliably generate JSON")
        print("   → Consider: Larger model, better prompts, or API fallback")
```

#### Step 3: Run Spike

```bash
# Make executable
chmod +x tests/spikes/hello_world.py

# Run spike
python tests/spikes/hello_world.py
```

**Example Output**:
```
============================================================
Run #1: Generating objectives for 'Python functions'
============================================================
Raw LLM Output:
{
  "topic": "Python functions",
  "objectives": [
    {
      "id": "LO-001",
      "verb": "define",
      "content": "What a function is in Python",
      "level": "Remember"
    }
  ]
}

✅ SUCCESS: Valid JSON generated!
   Topic: Python functions
   Objectives: 1
   Saved to: logs/spikes/run_1_success.json
...

============================================================
SPIKE RESULTS SUMMARY
============================================================
Valid JSON: 3/5
Validity Rate: 60.0%

✅ SPIKE PASSED: Model can generate valid JSON
   → Proceed with Test-First development
```

#### Step 4: Document Findings

Create [`docs/spike_results.md`](docs/spike_results.md):

```markdown
# Spike Results: DeepSeek-R1 JSON Generation

**Date**: 2025-01-05
**Model**: deepseek-r1:1.5b
**Question**: Can the model generate valid JSON matching CourseStructure schema?

## Results
- Validity Rate: 60% (3/5 attempts)
- Average Time: 18 seconds per generation
- Common Failures:
  - 2/5 attempts had trailing text after JSON
  - Model sometimes added markdown code blocks (```json ... ```)

## Recommendations
1. Use DSPy's TypedPredictor for stricter JSON enforcement
2. Add post-processing to strip markdown code blocks
3. Implement retry logic (3 attempts max)
4. Proceed with Test-First development for mocks, Test-After for real LLM

## Artifacts
- Successful outputs: `logs/spikes/run_1_success.json`
- Failed outputs: `logs/spikes/run_2_failed.txt`
```

#### Step 5: Decide Next Steps

Based on spike results:

- **60%+ validity** → Proceed with implementation, add retry logic
- **< 60% validity** → Try larger model or switch to OpenAI API temporarily
- **Too slow (> 30s)** → Consider quantized model or caching

---

## Phase 3: Test-After Workflow (Integration Tests)

**Use for**: Real LLM integration tests, API endpoint tests

### When to Write Tests AFTER Code

**ONLY AFTER**:
1. Spike proves LLM works
2. You have 3-5 real output examples
3. Mocked tests are all passing
4. Implementation is basically working

### Step-by-Step Process

#### 1. Implement Feature First

Write the code WITHOUT tests (gasp!):

```bash
# Implement DSPy module
vim src/modules/architect.py
```

```python
import dspy
from src.core.models import CourseStructure

class Architect(dspy.Module):
    """Generate learning objectives for a topic."""

    def forward(self, topic: str, target_audience: str) -> CourseStructure:
        # ... implementation ...

        # Call LLM
        response = self.llm(prompt)

        # Parse response
        parsed = json.loads(response.response)

        # Validate and return
        return CourseStructure(**parsed)
```

#### 2. Manually Test It

```bash
# Run manually with different inputs
python -c "
from src.modules.architect import Architect
arch = Architect()
result = arch.generate('Python functions', 'Developers')
print(result)
"
```

#### 3. Save Real Outputs

Create `tests/golden_set.json`:

```json
{
  "python_functions": {
    "input": {
      "topic": "Python functions",
      "target_audience": "Intermediate Python developers"
    },
    "output": {
      "topic": "Python functions",
      "objectives": [
        {
          "id": "LO-001",
          "verb": "define",
          "content": "What a function is and how it's defined",
          "level": "Remember"
        }
      ]
    }
  }
}
```

#### 4. Write Tests Based on Real Outputs

```bash
# Write integration test
vim tests/integration/test_architect_integration.py
```

```python
import pytest
from src.modules.architect import Architect
from src.core.models import CourseStructure

@pytest.mark.integration
@pytest.mark.slow
class TestArchitectIntegration:
    """Test real Ollama integration."""

    @pytest.fixture
    def architect(self):
        return Architect()

    def test_generate_python_objectives(self, architect):
        """Should generate objectives similar to golden set."""
        result = architect.generate(
            topic="Python functions",
            target_audience="Intermediate Python developers"
        )

        # Structure validation
        assert isinstance(result, CourseStructure)
        assert len(result.objectives) >= 3

        # Content validation (based on real outputs)
        levels = {obj.level for obj in result.objectives}
        assert len(levels) >= 2  # Should use multiple Bloom levels

        # Verb validation
        for obj in result.objectives:
            assert len(obj.verb) > 0
            assert len(obj.content) > 10  # Not just gibberish
```

#### 5. Run Tests (Expect Some Failures)

```bash
pytest tests/integration/ -v
```

#### 6. Fix Failures and Iterate

Adjust implementation or test expectations based on reality.

---

## Common TDD Mistakes to Avoid

### ❌ Mistake 1: Writing Too Many Tests at Once

**Bad**:
```bash
# Write 20 tests, then try to implement
vim tests/test_everything.py  # 500 lines of tests
```

**Good**:
```bash
# Write 1-2 tests, implement, repeat
vim tests/test_models.py  # Add test_verb_validation()
# → Implement
# → Add test_distractor_uniqueness()
# → Implement
```

### ❌ Mistake 2: Skipping the RED Phase

**Bad**:
```python
# Write implementation AND tests at same time
vim src/core/models.py  # Full implementation
vim tests/test_models.py  # Tests that already pass
```

**Good**:
```bash
# 1. Write test (run it - fails)
vim tests/test_models.py
pytest tests/test_models.py  # FAILED ✗

# 2. Write implementation (run test - passes)
vim src/core/models.py
pytest tests/test_models.py  # PASSED ✓
```

### ❌ Mistake 3: Testing Implementation Details

**Bad**:
```python
def test_function_calls_internal_helper(self):
    """Tests HOW code works (brittle)."""
    obj = MyClass()
    assert obj._internal_helper_called == True  # Bad!
```

**Good**:
```python
def test_function_produces_correct_output(self):
    """Tests WHAT code does (robust)."""
    obj = MyClass()
    result = obj.process(input_data)
    assert result == expected_output  # Good!
```

### ❌ Mistake 4: Not Refactoring

**Bad**:
```python
# Tests pass, but code is ugly
def calculate(x, y):
    # 50 lines of messy code
    result = (x * 2 + y / 3 - 4) % 10  # Yuck
    return result
```

**Good**:
```python
# Tests pass, refactor to clean up
def calculate(x, y):
    return normalize(double_and_add(x, y))

# Tests still pass! ✓
```

### ❌ Mistake 5: Testing Third-Party Libraries

**Bad**:
```python
def test_pydantic_validation_works(self):
    """Don't test Pydantic - they test it!"""
    obj = MyModel(field="value")
    assert obj.field == "value"  # Redundant
```

**Good**:
```python
def test_custom_validation_logic(self):
    """Test YOUR validation logic."""
    with pytest.raises(ValidationError):
        MyModel(field="invalid")  # Your custom rules
```

---

## Troubleshooting When Tests Won't Pass

### Problem 1: Test Passes Locally, Fails in CI

**Diagnosis**:
```bash
# Check environment differences
pytest --collect-only  # See which tests are found
python -c "import sys; print(sys.path)"  # Check PYTHONPATH
```

**Fix**:
```bash
# Ensure relative imports work
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
# Or use proper package structure
```

### Problem 2: Mocked Tests Pass, Integration Tests Fail

**Diagnosis**: Mock doesn't match real behavior

**Fix**:
```python
# Update mock to match real LLM output
@pytest.fixture
def mock_ollama_response(self):
    return Mock(
        response='{"topic": "Test", "objectives": []}',  # Match real format
        done=True
    )
```

### Problem 3: Flaky Tests (Sometimes Pass, Sometimes Fail)

**Diagnosis**: Non-deterministic behavior (LLM, timing, randomness)

**Fix**:
```python
# Use fixed seeds for randomness
import random
random.seed(42)

# Increase timeout for slow LLM
@pytest.mark.timeout(60)
def test_slow_generation(self):
    ...

# Or retry flaky tests
@pytest.mark.flaky(reruns=3)
def test_sometimes_fails(self):
    ...
```

### Problem 4: All Tests Fail After Refactor

**Diagnosis**: Changed behavior, not just implementation

**Fix**:
```bash
# Git diff to see what changed
git diff HEAD~1 src/core/models.py

# If behavior intentionally changed, update tests
# If accidental, revert or fix implementation
```

---

## Checklist Before Committing

### Pre-Commit Checklist

Run this before EVERY commit:

```bash
# 1. Fast tests (unit + mocked) - MUST PASS
pytest tests/unit/ tests/mocked/ -v

# 2. Check coverage - MUST BE > 75%
pytest --cov=src --cov-report=term-missing

# 3. Format code (optional)
black src/ tests/

# 4. Lint code (optional)
flake8 src/ tests/

# 5. Type check (optional)
mypy src/
```

### Pre-Push Checklist

Run this BEFORE pushing to remote:

```bash
# 1. Full test suite including slow tests
pytest -v

# 2. Integration tests with real LLM
pytest tests/integration/ -v

# 3. End-to-end tests
pytest tests/e2e/ -v

# 4. Verify Ollama still works
ollama run deepseek-r1:1.5b "Test"
```

### Commit Message Template

```bash
# Use conventional commit format
git commit -m "feat: add Bloom's verb validation

- Implement BloomsTaxonomy class
- Add verb validation for all 6 levels
- Test coverage: 95%
- Closes #12

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

---

## Quick Reference Commands

```bash
# Run only fast tests (default)
pytest

# Run with verbose output
pytest -v

# Run specific test file
pytest tests/unit/test_models.py

# Run specific test
pytest tests/unit/test_models.py::TestQuizQuestion::test_distractors_must_be_unique

# Run until first failure
pytest -x

# Run last failed tests
pytest --lf

# Drop into debugger on failure
pytest --pdb

# Generate coverage report
pytest --cov=src --cov-report=html

# Run marked tests only
pytest -m "not slow"

# Run integration tests only
pytest tests/integration/ -v -s
```

---

## Next Steps

1. **Start with Phase 1** (Test-First for schemas)
2. **Do spike** for LLM integration (Phase 2)
3. **Add integration tests** after spike succeeds (Phase 3)
4. **Refactor continuously** while keeping tests green
5. **Commit frequently** with pre-commit hooks

Remember: **Tests are your safety net**. They give you confidence to refactor and prevent regressions.
