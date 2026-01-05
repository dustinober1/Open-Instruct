# DSPy Prompt Strategy Guide

**Audience**: Junior Developers
**Purpose**: Complete guide to writing and optimizing DSPy prompts for Open-Instruct
**Prerequisite**: Read [Blooms_Taxonomy_Specification.md](Blooms_Taxonomy_Specification.md)

---

## Table of Contents
1. [DSPy Prompting Philosophy](#dspy-prompting-philosophy)
2. [Core DSPy Concepts](#core-dspy-concepts)
3. [Signature Definitions](#signature-definitions)
4. [Prompt Engineering Strategies](#prompt-engineering-strategies)
5. [Complete Prompt Templates](#complete-prompt-templates)
6. [Assertion & Constraint Enforcement](#assertion--constraint-enforcement)
7. [Prompt Optimization Workflow](#prompt-optimization-workflow)
8. [Common Prompt Failures & Fixes](#common-prompt-failures--fixes)

---

## DSPy Prompting Philosophy

### Why DSPy Instead of Raw Prompts?

**Traditional Prompting** ❌:
```python
prompt = "Generate 5 learning objectives about Python"
response = llm(prompt)  # Unstructured output, hard to validate
```

**DSPy Prompting** ✅:
```python
class GenerateObjectives(dspy.Signature):
    """Generate structured learning objectives."""
    topic = dspy.InputField(desc="The course topic")
    objectives = dspy.OutputField(desc="CourseStructure JSON")

result = GenerateObjectives(topic="Python")  # Typed, validated
```

**Benefits**:
- **Type Safety**: Output must match Pydantic schema
- **Separation of Concerns**: Prompt logic separate from LLM calls
- **Optimizability**: Easy to A/B test prompts
- **Retriability**: Assertions enforce constraints

### Our Prompt Strategy

```
┌─────────────────────────────────────────────────────┐
│ 1. STRUCTURE FIRST                                  │
│    Define signatures before prompts                │
└─────────────────────────────────────────────────────┘
                      ↓
┌─────────────────────────────────────────────────────┐
│ 2. VERB ENFORCEMENT                                 │
│    Hardcode Bloom's verbs in instructions          │
└─────────────────────────────────────────────────────┘
                      ↓
┌─────────────────────────────────────────────────────┐
│ 3. SCHEMA DRIVEN                                    │
│    Pydantic models define expected output           │
└─────────────────────────────────────────────────────┘
                      ↓
┌─────────────────────────────────────────────────────┐
│ 4. ASSERTION BACKED                                 │
│    Validate verbs, JSON structure, counts           │
└─────────────────────────────────────────────────────┘
                      ↓
┌─────────────────────────────────────────────────────┐
│ 5. RETRY ENABLED                                    │
│    Auto-retry with stronger constraints             │
└─────────────────────────────────────────────────────┘
```

---

## Core DSPy Concepts

### 1. Signatures

A **Signature** defines the input/output contract:

```python
import dspy

class GenerateObjectives(dspy.Signature):
    """Generate learning objectives using Bloom's Taxonomy."""

    # Input fields
    topic = dspy.InputField(
        desc="The main subject/topic for the course",
        type=str
    )

    target_audience = dspy.InputField(
        desc="Who will be learning (e.g., 'Grade 10 students', 'Senior Developers')",
        type=str
    )

    # Output field
    objectives = dspy.OutputField(
        desc="CourseStructure with 5-10 learning objectives",
        type=CourseStructure  # Pydantic model!
    )
```

### 2. Modules

A **Module** implements the signature with prompt logic:

```python
class Architect(dspy.Module):
    """Generate learning objectives for a given topic."""

    def __init__(self):
        super().__init__()
        # Use TypedPredictor for structured outputs
        self.generate = dspy.TypedPredictor(GenerateObjectives)

    def forward(self, topic: str, target_audience: str = "General learners") -> CourseStructure:
        # DSPy automatically constructs prompt from Signature
        result = self.generate(topic=topic, target_audience=target_audience)
        return result.objectives
```

### 3. Assertions

**Assertions** validate outputs and enable retries:

```python
@dspy.assertion
def verbs_match_blooms_level(output: CourseStructure) -> bool:
    """All verbs must be valid for their Bloom's level."""
    for obj in output.objectives:
        if not BloomsTaxonomy.validate_verb(obj.verb, obj.level):
            return False
    return True
```

---

## Signature Definitions

### Signature 1: GenerateObjectives

**Purpose**: Generate learning objectives for a topic

```python
# src/modules/architect.py

import dspy
from typing import List
from src.core.models import CourseStructure, LearningObjective, BloomLevel

class GenerateObjectives(dspy.Signature):
    """
    Generate a structured set of learning objectives using Bloom's Taxonomy.

    You must produce valid JSON matching the CourseStructure schema.
    """

    # Inputs
    topic = dspy.InputField(
        desc="The main subject/topic (e.g., 'Python functions', 'World War II')"
    )

    target_audience = dspy.InputField(
        desc="Target learner persona (e.g., 'Intermediate Python developers', 'High school students')"
    )

    num_objectives = dspy.InputField(
        desc="Number of objectives to generate (5-10 recommended)",
        type=int,
        default=6
    )

    # Output
    course = dspy.OutputField(
        desc="Complete CourseStructure with validated Bloom's verbs",
        type=CourseStructure
    )
```

### Signature 2: GenerateQuiz

**Purpose**: Generate a quiz question for a learning objective

```python
# src/modules/assessor.py

class GenerateQuiz(dspy.Signature):
    """
    Generate a multiple-choice quiz question for a learning objective.

    Must include:
    - 1 correct answer
    - 3 distinct distractors (wrong but plausible)
    - Explanation for why answer is correct
    """

    # Inputs
    objective = dspy.InputField(
        desc="The learning objective to assess",
        type=LearningObjective
    )

    difficulty = dspy.InputField(
        desc="Quiz difficulty: 'easy', 'medium', or 'hard'",
        type=str,
        default="medium"
    )

    # Output
    quiz = dspy.OutputField(
        desc="QuizQuestion with exactly 4 unique options",
        type=QuizQuestion
    )
```

### Signature 3: IdentifyPrerequisites

**Purpose**: Identify prerequisite dependencies between objectives

```python
# src/modules/curriculum.py

class IdentifyPrerequisites(dspy.Signature):
    """
    Identify which learning objectives are prerequisites for others.

    Output Format:
    {
        "LO-003": ["LO-001", "LO-002"],
        "LO-005": ["LO-004"]
    }

    Meaning: LO-003 requires LO-001 and LO-002 first
    """

    # Inputs
    objectives = dspy.InputField(
        desc="List of learning objective dictionaries",
        type=List[dict]
    )

    # Output
    dependencies = dspy.OutputField(
        desc="Dictionary mapping objective_id to list of prerequisite IDs",
        type=dict
    )
```

---

## Prompt Engineering Strategies

### Strategy 1: Schema-First Prompting

**Problem**: LLM generates invalid JSON
**Solution**: Show example of expected schema in prompt

```python
class GenerateObjectives(dspy.Signature):
    """Generate learning objectives using Bloom's Taxonomy.

    CRITICAL: Output MUST be valid JSON matching this EXACT structure:

    {
        "topic": "Python Functions",
        "objectives": [
            {
                "id": "LO-001",
                "verb": "define",
                "content": "what a function is",
                "level": "Remember"
            }
        ]
    }

    Requirements:
    - id: Must be "LO-XXX" format (e.g., LO-001, LO-002)
    - verb: MUST be from approved Bloom's verb list for the level
    - level: One of [Remember, Understand, Apply, Analyze, Evaluate, Create]
    - content: Clear, specific learning outcome (10-30 words)

    Remember: Do NOT include any text outside the JSON. No markdown, no explanations.
    """

    topic = dspy.InputField(desc="Course topic")
    target_audience = dspy.InputField(desc="Target learners")
    course = dspy.OutputField(desc="Valid JSON CourseStructure")
```

### Strategy 2: Verb Enforcement in Prompt

**Problem**: LLM uses invalid verbs for Bloom's level
**Solution**: List approved verbs directly in prompt

```python
class GenerateObjectives(dspy.Signature):
    """Generate learning objectives using Bloom's Taxonomy.

    BLOOM'S TAXONOMY VERBS (USE ONLY THESE):

    Remember: define, list, name, identify, recall, recognize, label, match, ...
    Understand: explain, describe, summarize, interpret, paraphrase, clarify, ...
    Apply: apply, use, implement, execute, employ, utilize, practice, perform, ...
    Analyze: analyze, differentiate, distinguish, examine, investigate, inspect, ...
    Evaluate: evaluate, assess, judge, appraise, rate, score, value, critique, ...
    Create: create, design, construct, build, develop, formulate, generate, ...

    CRITICAL: Each objective MUST use a verb from the corresponding level's list.
    Do NOT use verbs from other levels (e.g., don't use "create" for Remember level).
    """

    topic = dspy.InputField(desc="Course topic")
    course = dspy.OutputField(desc="Validated CourseStructure")
```

### Strategy 3: Progressive Complexity

**Problem**: LLM generates all objectives at same difficulty
**Solution**: Specify level progression

```python
class GenerateObjectives(dspy.Signature):
    """Generate learning objectives using Bloom's Taxonomy.

    PROGRESSION REQUIREMENT:
    Your objectives MUST progress through Bloom's levels:

    1-2 objectives: Remember (basic facts)
    1-2 objectives: Understand (comprehension)
    1-2 objectives: Apply (using knowledge)
    0-1 objectives: Analyze (breaking down)
    0-1 objectives: Evaluate (judging)
    0-1 objectives: Create (producing something new)

    Example for "Python Functions":
    - LO-001 [Remember]: Define what a function is
    - LO-002 [Understand]: Explain function parameters
    - LO-003 [Apply]: Write a simple function
    - LO-004 [Analyze]: Compare positional vs keyword arguments
    - LO-005 [Evaluate]: Assess when to use functions
    - LO-006 [Create]: Design a modular program using functions

    Start simple, end complex.
    """

    topic = dspy.InputField(desc="Course topic")
    course = dspy.OutputField(desc="Progressive CourseStructure")
```

### Strategy 4: Few-Shot Examples

**Problem**: LLM doesn't understand expected format
**Solution**: Provide examples in prompt

```python
class GenerateQuiz(dspy.Signature):
    """Generate a multiple-choice quiz question.

    EXAMPLE OUTPUT (follow this format EXACTLY):

    {
        "stem": "What is the output of print(2 + 3)?",
        "correct_answer": "5",
        "distractors": ["2", "6", "Error"],
        "explanation": "In Python, 2 + 3 equals 5"
    }

    REQUIREMENTS:
    - stem: Clear question (10-30 words)
    - correct_answer: Single correct choice (short, 1-5 words)
    - distractors: EXACTLY 3 wrong choices (must be plausible but clearly wrong)
    - explanation: Why correct answer is right (10-30 words)

    QUALITY CHECKLIST:
    ✓ Distractors are plausible (e.g., common mistakes)
    ✓ Only one answer is unambiguously correct
    ✓ Distractors are distinct (no duplicates)
    ✓ Explanation helps learner understand
    """

    objective = dspy.InputField(desc="Learning objective to assess")
    quiz = dspy.OutputField(desc="Valid QuizQuestion")
```

---

## Complete Prompt Templates

### Template 1: Architect Module (Objectives)

```python
# src/modules/architect.py

import dspy
from typing import List
from src.core.models import CourseStructure, BloomLevel, BloomsTaxonomy

class Architect(dspy.Module):
    """Generate learning objectives using DSPy with strict validation."""

    def __init__(self, num_retries: int = 3):
        super().__init__()
        self.num_retries = num_retries

        # Configure TypedPredictor with retries
        self.generate = dspy.TypedPredictor(GenerateObjectives)

    def forward(self, topic: str, target_audience: str = "General learners") -> CourseStructure:
        """Generate objectives with retry logic."""

        # Construct the prompt (DSPy does this automatically from Signature)
        for attempt in range(self.num_retries):
            try:
                result = self.generate(
                    topic=topic,
                    target_audience=target_audience
                )

                # Validate output
                self._validate_objectives(result.course)

                return result.course

            except Exception as e:
                if attempt == self.num_retries - 1:
                    # Final attempt failed
                    raise ValueError(f"Failed after {self.num_retries} attempts: {e}")

                # Retry with stronger constraints
                self._strengthen_prompt()

    def _validate_objectives(self, course: CourseStructure):
        """Validate generated objectives against constraints."""

        # Check 1: Minimum objective count
        if len(course.objectives) < 5:
            raise ValueError(f"Too few objectives: {len(course.objectives)} (minimum 5)")

        # Check 2: All verbs must match levels
        for obj in course.objectives:
            if not BloomsTaxonomy.validate_verb(obj.verb, obj.level):
                raise ValueError(
                    f"Invalid verb '{obj.verb}' for level {obj.level}. "
                    f"Use verbs from: {BloomsTaxonomy.VERBS.get(obj.level, [])[:5]}..."
                )

        # Check 3: Unique objective IDs
        ids = [obj.id for obj in course.objectives]
        if len(ids) != len(set(ids)):
            raise ValueError("Duplicate objective IDs detected")

        # Check 4: Level progression (should advance through Bloom's)
        levels = [obj.level for obj in course.objectives]
        level_order = {
            BloomLevel.REMEMBER: 1,
            BloomLevel.UNDERSTAND: 2,
            BloomLevel.APPLY: 3,
            BloomLevel.ANALYZE: 4,
            BloomLevel.EVALUATE: 5,
            BloomLevel.CREATE: 6
        }

        # Check that levels generally increase (not strict, but should trend up)
        level_indices = [level_order[l] for l in levels]
        if level_indices[-1] <= level_indices[0]:
            # Last objective is same or lower level than first
            raise ValueError("Objectives should progress to higher Bloom's levels")

    def _strengthen_prompt(self):
        """Add stronger constraints for retry attempt."""
        # DSPy will automatically include the signature instructions
        # This method can modify the signature dynamically for retries
        pass
```

### Template 2: Assessor Module (Quizzes)

```python
# src/modules/assessor.py

import dspy
from src.core.models import QuizQuestion, LearningObjective

class Assessor(dspy.Module):
    """Generate quiz questions with validated distractors."""

    def __init__(self):
        super().__init__()
        self.generate = dspy.TypedPredictor(GenerateQuiz)

    def forward(self, objective: LearningObjective, difficulty: str = "medium") -> QuizQuestion:
        """Generate quiz for a learning objective."""

        # Generate with retries
        for attempt in range(3):
            try:
                result = self.generate(
                    objective=objective,
                    difficulty=difficulty
                )

                # Validate quiz
                self._validate_quiz(result.quiz)

                return result.quiz

            except Exception as e:
                if attempt == 2:
                    raise ValueError(f"Failed to generate valid quiz: {e}")

    def _validate_quiz(self, quiz: QuizQuestion):
        """Validate generated quiz."""

        # Check 1: Exactly 3 distractors
        if len(quiz.distractors) != 3:
            raise ValueError(f"Need exactly 3 distractors, got {len(quiz.distractors)}")

        # Check 2: Distractors are unique
        if len(quiz.distractors) != len(set(quiz.distractors)):
            raise ValueError("Distractors must be unique")

        # Check 3: Correct answer not in distractors
        if quiz.correct_answer in quiz.distractors:
            raise ValueError("Correct answer must not be in distractors")

        # Check 4: All options reasonable length
        all_options = [quiz.correct_answer] + quiz.distractors
        for opt in all_options:
            if len(opt) < 1:
                raise ValueError("Options cannot be empty")
            if len(opt) > 100:
                raise ValueError(f"Option too long: {len(opt)} chars (max 100)")

        # Check 5: Stem is a question
        if not quiz.stim.strip().endswith('?'):
            raise ValueError("Quiz stem must end with '?'")
```

---

## Assertion & Constraint Enforcement

### Using DSPy Assertions

```python
# src/modules/architect.py

import dspy
from src.core.models import BloomsTaxonomy

# Assertion 1: Verb Validation
@dspy.assertion
def verbs_match_level(output: CourseStructure) -> bool:
    """All verbs must be valid for their Bloom's level."""
    for obj in output.objectives:
        if not BloomsTaxonomy.validate_verb(obj.verb, obj.level):
            dspy.Suggest(
                verb=BloomsTaxonomy.get_random_verb(obj.level)
            )
            return False
    return True

# Assertion 2: Objective Count
@dspy.assertion
def sufficient_objectives(output: CourseStructure) -> bool:
    """Must generate at least 5 objectives."""
    return len(output.objectives) >= 5

# Assertion 3: Unique IDs
@dspy.assertion
def unique_objective_ids(output: CourseStructure) -> bool:
    """All objective IDs must be unique."""
    ids = [obj.id for obj in output.objectives]
    return len(ids) == len(set(ids))

# Apply assertions to module
class Architect(dspy.Module):
    def __init__(self):
        super().__init__()
        self.generate = dspy.TypedPredictor(GenerateObjectives)

        # Configure assertions with backtrack suggestions
        dspy.settings.configure(
            assertions=[
                verbs_match_level,
                sufficient_objectives,
                unique_objective_ids
            ],
            max_backtrack_attempts=3
        )

    def forward(self, topic: str) -> CourseStructure:
        # DSPy will automatically retry if assertions fail
        result = self.generate(topic=topic)
        return result.course
```

### Constraint: Bloom's Verb Enforcement

```python
# src/modules/constraints.py

from typing import List
import dspy

class EnforceBloomsVerbs(dspy.Constraint):
    """
    Ensure LLM only uses approved Bloom's verbs.

    If invalid verb detected, automatically replace with valid one.
    """

    def __init__(self):
        super().__init__()
        self.taxonomy = BloomsTaxonomy()

    def validate(self, output: CourseStructure) -> bool:
        """Check if all verbs are valid."""
        for obj in output.objectives:
            if not self.taxonomy.validate_verb(obj.verb, obj.level):
                # Try to fix it
                obj.verb = self.taxonomy.get_random_verb(obj.level)

        return True

# Use in module
class Architect(dspy.Module):
    def __init__(self):
        super().__init__()
        self.generate = dspy.TypedPredictor(GenerateObjectives)
        self.constraint = EnforceBloomsVerbs()

    def forward(self, topic: str) -> CourseStructure:
        result = self.generate(topic=topic)

        # Apply constraint
        self.constraint.validate(result.course)

        return result.course
```

---

## Prompt Optimization Workflow

### Step 1: Baseline Prompt

Start simple:

```python
class GenerateObjectives(dspy.Signature):
    """Generate learning objectives."""
    topic = dspy.InputField(desc="Topic")
    objectives = dspy.OutputField(desc="List of objectives")
```

**Test**: Run 10 iterations, measure JSON validity rate

### Step 2: Add Schema

Add structure:

```python
class GenerateObjectives(dspy.Signature):
    """Generate learning objectives.

    Output must match this schema:
    {"topic": "...", "objectives": [...]}
    """
    topic = dspy.InputField(desc="Topic")
    objectives = dspy.OutputField(desc="Valid JSON CourseStructure")
```

**Test**: Run 10 iterations, validity should improve

### Step 3: Add Verb Lists

Add constraints:

```python
class GenerateObjectives(dspy.Signature):
    """Generate learning objectives.

    Use ONLY these verbs:
    Remember: define, list, name, identify...
    (etc)
    """
    topic = dspy.InputField(desc="Topic")
    objectives = dspy.OutputField(desc="Validated CourseStructure")
```

**Test**: Run 10 iterations, measure verb alignment

### Step 4: Add Examples

Add few-shot:

```python
class GenerateObjectives(dspy.Signature):
    """Generate learning objectives.

    Example output:
    {
        "topic": "Python Functions",
        "objectives": [
            {"id": "LO-001", "verb": "define", "content": "...", "level": "Remember"}
        ]
    }
    """
    topic = dspy.InputField(desc="Topic")
    objectives = dspy.OutputField(desc="Validated CourseStructure")
```

**Test**: Run 10 iterations, measure quality

### Step 5: Add Assertions

Add validation:

```python
@dspy.assertion
def verbs_match_level(output):
    for obj in output.objectives:
        if not BloomsTaxonomy.validate_verb(obj.verb, obj.level):
            return False
    return True

# Configure module
dspy.settings.configure(assertions=[verbs_match_level])
```

**Test**: Run 10 iterations, measure auto-correction rate

---

## Common Prompt Failures & Fixes

### Failure 1: LLM Ignores JSON Format

**Symptom**: Output includes markdown or explanatory text

```
❌ BAD:
Here's the JSON you requested:
```json
{"topic": "Python", ...}
```
```

**Fix 1**: Explicit instruction
```python
"""Generate learning objectives.

CRITICAL: Return ONLY raw JSON. No markdown, no explanations, no extra text.
Output format: {"topic": "...", "objecties": [...]}
"""
```

**Fix 2**: Post-processing
```python
def extract_json(raw_output: str) -> str:
    """Extract JSON from LLM output."""
    # Remove markdown code blocks
    raw_output = raw_output.strip()
    if raw_output.startswith('```'):
        # Find the JSON portion
        lines = raw_output.split('\n')
        json_lines = []
        in_code_block = False
        for line in lines:
            if line.startswith('```'):
                in_code_block = not in_code_block
                continue
            if in_code_block:
                json_lines.append(line)
        return '\n'.join(json_lines)

    return raw_output
```

### Failure 2: Invalid Bloom's Verbs

**Symptom**: Uses "create" for Remember level

**Fix**: Add verb validation with fallback
```python
def fix_invalid_verbs(course: CourseStructure) -> CourseStructure:
    """Replace invalid verbs with valid ones."""
    for obj in course.objectives:
        if not BloomsTaxonomy.validate_verb(obj.verb, obj.level):
            # Log the issue
            logger.warning(
                f"Invalid verb '{obj.verb}' for {obj.level}, "
                f"replacing with valid verb"
            )

            # Replace with random valid verb
            obj.verb = BloomsTaxonomy.get_random_verb(obj.level)

    return course
```

### Failure 3: Too Few Objectives

**Symptom**: Generates only 2-3 objectives instead of 5+

**Fix**: Explicit count requirement
```python
"""Generate learning objectives.

REQUIREMENT: Generate EXACTLY 6 objectives.
- 2 at Remember level
- 2 at Understand level
- 1 at Apply level
- 1 at Create level

Do NOT generate fewer than 6 objectives.
"""
```

**Fix 2**: Retry with higher temperature
```python
# On retry, increase temperature for more variety
lm = dspy.lm.Ollama(model="deepseek-r1:1.5b", temperature=0.8)
```

### Failure 4: Duplicate Objective IDs

**Symptom**: Multiple objectives have ID "LO-001"

**Fix**: Add uniqueness constraint
```python
"""Generate learning objectives.

REQUIREMENT: Each objective must have a UNIQUE ID.
Format: LO-001, LO-002, LO-003, etc.
Do NOT repeat IDs.
"""
```

**Fix 2**: Post-processing
```python
def ensure_unique_ids(course: CourseStructure) -> CourseStructure:
    """Ensure all objective IDs are unique."""
    seen_ids = set()

    for i, obj in enumerate(course.objectives, start=1):
        # Check if ID already seen
        if obj.id in seen_ids:
            # Generate new unique ID
            obj.id = f"LO-{i:03d}"

        seen_ids.add(obj.id)

    return course
```

---

## Measuring Prompt Effectiveness

### Metrics to Track

```python
# src/modules/metrics.py

class PromptMetrics:
    """Track prompt performance over time."""

    def __init__(self):
        self.attempts = []
        self.successes = []
        self.failures = []

    def record_attempt(self, success: bool, validity_rate: float, time_seconds: float):
        """Record a generation attempt."""
        self.attempts.append({
            "success": success,
            "validity_rate": validity_rate,
            "time": time_seconds,
            "timestamp": datetime.now()
        })

        if success:
            self.successes.append(validity_rate)
        else:
            self.failures.append(validity_rate)

    def get_summary(self):
        """Get performance summary."""
        return {
            "total_attempts": len(self.attempts),
            "success_rate": len(self.successes) / len(self.attempts) if self.attempts else 0,
            "avg_validity_rate": sum(self.successes) / len(self.successes) if self.successes else 0,
            "avg_time": sum(a["time"] for a in self.attempts) / len(self.attempts) if self.attempts else 0
        }
```

### Target Metrics

| Metric | Target | Notes |
|--------|--------|-------|
| JSON Validity Rate | ≥ 80% | 8/10 outputs parse successfully |
| Verb Alignment | ≥ 90% | 9/10 verbs match Bloom's level |
| Average Generation Time | < 20s | Per objective (with local LLM) |
| Retry Success Rate | ≥ 60% | Retries that fix invalid outputs |

---

## Quick Reference: Prompt Templates

### Template for Objectives Generation

```python
GENERATE_OBJECTIVES_PROMPT = """
Generate {num} learning objectives about: {topic}

Target audience: {audience}

CRITICAL REQUIREMENTS:
1. Output MUST be valid JSON (no markdown, no extra text)
2. Use ONLY approved Bloom's verbs for each level
3. Progress from simple (Remember) to complex (Create)
4. Each objective must have unique ID (LO-001, LO-002, etc.)

APPROVED VERBS:
Remember: {remember_verbs}
Understand: {understand_verbs}
Apply: {apply_verbs}
Analyze: {analyze_verbs}
Evaluate: {evaluate_verbs}
Create: {create_verbs}

OUTPUT FORMAT:
{{
    "topic": "{topic}",
    "objectives": [
        {{
            "id": "LO-001",
            "verb": "define",
            "content": "what the topic is",
            "level": "Remember"
        }}
    ]
}}
"""
```

### Template for Quiz Generation

```python
GENERATE_QUIZ_PROMPT = """
Generate a {difficulty} multiple-choice question for:

Objective: {objective_text}
Level: {bloom_level}

REQUIREMENTS:
1. Question stem must be clear and concise
2. Exactly 4 options (1 correct + 3 distractors)
3. Distractors must be plausible but clearly wrong
4. Include explanation for correct answer
5. Output valid JSON only

OUTPUT FORMAT:
{{
    "stem": "Question text?",
    "correct_answer": "Correct option",
    "distractors": ["Wrong 1", "Wrong 2", "Wrong 3"],
    "explanation": "Why the answer is correct"
}}
"""
```

---

## Next Steps

1. **Copy prompt templates** into your DSPy modules
2. **Implement assertions** for verb validation
3. **Add retry logic** with constraint strengthening
4. **Track metrics** for each generation attempt
5. **Optimize iteratively** based on failure patterns

Remember: **Prompts are code**. Version them, test them, and optimize them like any other part of the system.
