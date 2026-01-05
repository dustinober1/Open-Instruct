# 🤖 DSPy Usage: Code Examples

**Version**: 1.0.0
**Last Updated**: 2025-01-05

---

## 🚀 Introduction

This document provides practical examples for using DSPy (Declarative Self-improving Python) with the Open-Instruct project. DSPy helps you build and optimize complex LM pipelines.

---

## 📋 DSPy Basics

### What is DSPy?
DSPy is a framework for programming with foundation models that:
- **Structures prompts** with type hints
- **Optimizes prompts** automatically
- **Validates outputs** with assertions
- **Caches responses** for performance

### Key Concepts
- **Signatures**: Define input/output types
- **Modules**: Reusable LM components
- **Predictors**: Basic LM prediction
- **TypedPredictors**: Structured output prediction
- **Optimizers**: Prompt optimization

---

## 🛠️ Basic DSPy Examples

### Example 1: Simple Learning Objective Generation

```python
import dspy
from dspy import TypedPredictor, InputField, OutputField
from pydantic import BaseModel

# Define the signature for generating learning objectives
class ObjectiveSignature(dspy.Signature):
    """Generate a single learning objective using Bloom's Taxonomy."""

    # Input fields
    topic = InputField(desc="The educational topic")
    level = InputField(desc="Bloom's taxonomy level: remember, understand, apply, analyze, evaluate, create")

    # Output fields
    verb = OutputField(desc="Action verb appropriate for the level")
    objective = OutputField(desc="The complete learning objective statement")

# Create the predictor
generate_objective = TypedPredictor(ObjectiveSignature)

# Generate an objective
result = generate_objective(
    topic="Introduction to Python",
    level="understand"
)

print(f"Verb: {result.verb}")
print(f"Objective: {result.objective}")
```

### Example 2: Batch Objective Generation

```python
from typing import List

class BatchObjectiveSignature(dspy.Signature):
    """Generate multiple learning objectives for a topic."""

    topic = InputField(desc="The educational topic")
    count = InputField(desc="Number of objectives to generate", default=5)

    objectives = OutputField(desc="List of learning objectives")

class BatchObjectiveGenerator(dspy.Module):
    def __init__(self):
        self.generate = TypedPredictor(BatchObjectiveSignature)

    def forward(self, topic: str, count: int = 5):
        return self.generate(topic=topic, count=count)

# Create generator
generator = BatchObjectiveGenerator()

# Generate multiple objectives
result = generator(topic="Data Structures", count=6)

for i, objective in enumerate(result.objectives, 1):
    print(f"{i}. {objective}")
```

---

## 🎯 Advanced DSPy Examples

### Example 3: Bloom's Taxonomy Validator

```python
class BloomValidator(dspy.Signature):
    """Validate that generated objectives follow Bloom's Taxonomy rules."""

    objectives = InputField(desc="List of learning objectives to validate")
    violations = OutputField(desc="List of validation violations found")

class ObjectiveValidator(dspy.Module):
    def __init__(self):
        self.validate = TypedPredictor(BloomValidator)

    def forward(self, objectives: List[str]):
        result = self.validate(objectives=objectives)

        # Check for violations
        if result.violations:
            print("⚠️  Validation violations found:")
            for violation in result.violations:
                print(f"  - {violation}")

        return len(result.violations) == 0

# Create validator
validator = ObjectiveValidator()

# Example usage
objectives = [
    "Identify the basic syntax of Python",
    "Explain the difference between lists and tuples",
    "Create a web application using Flask"
]

is_valid = validator(objectives)
print(f"Validation result: {is_valid}")
```

### Example 4: DSPy with Caching

```python
import hashlib
from datetime import datetime, timedelta

class DSPyCache:
    """Simple cache for DSPy results."""

    def __init__(self):
        self.cache = {}

    def get_cache_key(self, signature: str, **kwargs):
        """Generate cache key from signature and arguments."""
        key_str = f"{signature}_{sorted(kwargs.items())}"
        return hashlib.md5(key_str.encode()).hexdigest()

    def get(self, cache_key: str):
        """Get cached result if available and not expired."""
        if cache_key in self.cache:
            result, timestamp = self.cache[cache_key]
            if datetime.now() - timestamp < timedelta(hours=1):  # 1 hour TTL
                return result
            else:
                del self.cache[cache_key]
        return None

    def set(self, cache_key: str, result):
        """Cache result with timestamp."""
        self.cache[cache_key] = (result, datetime.now())

# Use caching with DSPy
cache = DSPyCache()

def cached_predict(predictor, **kwargs):
    """Predict with caching."""
    signature = predictor.signature.__class__.__name__
    cache_key = cache.get_cache_key(signature, **kwargs)

    # Check cache first
    cached_result = cache.get(cache_key)
    if cached_result:
        print("🎯 Using cached result")
        return cached_result

    # Generate new result
    print("🔄 Generating new result")
    result = predictor(**kwargs)
    cache.set(cache_key, result)
    return result

# Example usage
predictor = TypedPredictor(ObjectiveSignature)
result = cached_predict(
    predictor,
    topic="Machine Learning Basics",
    level="apply"
)
```

---

## 🔄 DSPy Optimizers

### Example 5: Bootstrap Few-Shot Optimizer

```python
from dspy.teleprompters import BootstrapFewShot

# Define training data (few-shot examples)
trainset = [
    dspy.Example(
        topic="Introduction to Python",
        level="remember",
        verb="identify",
        objective="Identify the basic syntax and structure of Python programs"
    ),
    dspy.Example(
        topic="Python Variables",
        level="understand",
        verb="explain",
        objective="Explain the difference between variables, data types, and operators in Python"
    ),
    # Add more examples...
]

# Create the predictor
predictor = TypedPredictor(ObjectiveSignature)

# Set up optimizer
optimizer = BootstrapFewShot(metric=lambda example, pred, trace=None: True)

# Compile the predictor with optimization
compiled_predictor = optimizer.compile(
    predictor,
    trainset=trainset,
    num_trials=3
)

# Test the optimized predictor
result = compiled_predictor(
    topic="Object-Oriented Programming",
    level="analyze"
)

print(f"Optimized result: {result.objective}")
```

### Example 6: Bayesian Signature Optimizer

```python
from dspy.teleprompters import BayesianSignatureOptimizer

# Define signature space to explore
signature_space = [
    "Generate a learning objective about {topic} at {level} level",
    "Create a Bloom's Taxonomy-aligned learning objective for {topic} focusing on {level}",
    "Develop a {level}-level learning objective about {topic}"
]

# Set up optimizer
optimizer = BayesianSignatureOptimizer(
    metric=lambda example, pred, trace=None: True,
    num_candidate_programs=4,
    num_programs=1
)

# Optimize the prompt signature
optimized_predictor = optimizer.compile(
    TypedPredictor(ObjectiveSignature),
    trainset=trainset[:2],  # Use small training set
    num_trials=2
)

# Test optimized predictor
result = optimized_predictor(
    topic="Database Design",
    level="evaluate"
)

print(f"Optimized result: {result.objective}")
```

---

## 🧪 DSPy Testing Examples

### Example 7: Unit Testing DSPy Modules

```python
import pytest

class TestObjectiveGenerator:
    def setup_method(self):
        """Set up test fixtures."""
        self.generator = BatchObjectiveGenerator()
        self.validator = ObjectiveValidator()

    def test_generate_single_objective(self):
        """Test generating a single objective."""
        result = self.generator(
            topic="Python Basics",
            count=1
        )

        assert len(result.objectives) == 1
        assert "Python" in result.objectives[0]

    def test_generate_multiple_objectives(self):
        """Test generating multiple objectives."""
        result = self.generator(
            topic="Web Development",
            count=5
        )

        assert len(result.objectives) == 5
        assert all("Web Development" in obj for obj in result.objectives)

    def test_valid_objectives(self):
        """Test that generated objectives are valid."""
        objectives = [
            "Identify HTML tags",
            "Explain CSS selectors",
            "Apply JavaScript functions"
        ]

        is_valid = self.validator(objectives)
        assert is_valid == True

    def test_invalid_objectives(self):
        """Test handling of invalid objectives."""
        invalid_objectives = [
            "This is not a learning objective",
            "Another invalid statement"
        ]

        is_valid = self.validator(invalid_objectives)
        assert is_valid == False

    def test_caching(self):
        """Test that caching works."""
        predictor = TypedPredictor(ObjectiveSignature)
        cache = DSPyCache()

        # First call (should generate)
        result1 = cached_predict(
            predictor,
            topic="API Design",
            level="create"
        )

        # Second call (should use cache)
        result2 = cached_predict(
            predictor,
            topic="API Design",
            level="create"
        )

        assert result1.objective == result2.objective
```

### Example 8: Integration Testing

```python
class TestDSPyIntegration:
    def test_end_to_end_objective_generation(self):
        """Test complete objective generation workflow."""
        # Initialize components
        generator = BatchObjectiveGenerator()
        validator = ObjectiveValidator()

        # Generate objectives
        result = generator(
            topic="Machine Learning",
            count=5
        )

        # Validate objectives
        is_valid = validator(result.objectives)

        # Assertions
        assert len(result.objectives) == 5
        assert is_valid == True
        assert all("Machine Learning" in obj for obj in result.objectives)

    def test_error_handling(self):
        """Test error handling in DSPy modules."""
        predictor = TypedPredictor(ObjectiveSignature)

        # Test with invalid input
        with pytest.raises(Exception):
            predictor(topic="", level="invalid_level")
```

---

## 🎯 DSPy Best Practices

### 1. Use Type Hints
```python
# ✅ Good: Use clear type hints
class ObjectiveSignature(dspy.Signature):
    topic: str = InputField(desc="Educational topic")
    level: str = InputField(desc="Bloom's taxonomy level")
    verb: str = OutputField(desc="Action verb")
    objective: str = OutputField(desc="Learning objective")

# ❌ Bad: No type hints
class BadSignature(dspy.Signature):
    topic = InputField()
    level = InputField()
    verb = OutputField()
    objective = OutputField()
```

### 2. Add Descriptions
```python
# ✅ Good: Detailed descriptions
class DetailedSignature(dspy.Signature):
    """Generate Bloom's Taxonomy-aligned learning objectives for educational content."""

    topic = InputField(
        desc="The main subject or topic for the learning objectives. Example: 'Introduction to Python Programming'"
    )
    level = InputField(
        desc="The cognitive level from Bloom's Taxonomy: remember, understand, apply, analyze, evaluate, create. Example: 'apply'"
    )
    verb = OutputField(
        desc="An action verb appropriate for the specified cognitive level. Example: 'implement', 'solve', 'create'"
    )
    objective = OutputField(
        desc="A complete learning objective statement that starts with the action verb and describes what the learner should be able to do. Example: 'Implement a basic sorting algorithm'"
    )
```

### 3. Validate Outputs
```python
class ValidatedObjectiveGenerator(dspy.Module):
    def __init__(self):
        self.generate = TypedPredictor(ObjectiveSignature)
        self.validator = ObjectiveValidator()

    def forward(self, topic: str, level: str):
        # Generate objective
        result = self.generate(topic=topic, level=level)

        # Validate the objective
        is_valid = self.validator([result.objective])

        # Retry if invalid (simple retry strategy)
        max_retries = 3
        retry_count = 0

        while not is_valid and retry_count < max_retries:
            print(f"⚠️  Retry {retry_count + 1}: Objective validation failed")
            result = self.generate(topic=topic, level=level)
            is_valid = self.validator([result.objective])
            retry_count += 1

        if not is_valid:
            raise ValueError(f"Failed to generate valid objective after {max_retries} attempts")

        return result
```

### 4. Use Caching Wisely
```python
class CachedObjectiveGenerator(dspy.Module):
    def __init__(self, cache_ttl_hours: int = 24):
        self.generator = TypedPredictor(ObjectiveSignature)
        self.cache = {}
        self.cache_ttl = timedelta(hours=cache_ttl_hours)

    def _get_cache_key(self, topic: str, level: str) -> str:
        return hashlib.md5(f"{topic}_{level}".encode()).hexdigest()

    def _is_cache_valid(self, timestamp: datetime) -> bool:
        return datetime.now() - timestamp < self.cache_ttl

    def forward(self, topic: str, level: str):
        cache_key = self._get_cache_key(topic, level)

        # Check cache
        if cache_key in self.cache:
            result, timestamp = self.cache[cache_key]
            if self._is_cache_valid(timestamp):
                print("🎯 Using cached objective")
                return result

        # Generate new objective
        print("🔄 Generating new objective")
        result = self.generator(topic=topic, level=level)

        # Cache result
        self.cache[cache_key] = (result, datetime.now())

        return result
```

---

## 🔍 Debugging DSPy Issues

### Common Issues and Solutions

#### Issue 1: Invalid JSON Output
```python
# Problem: DSPy returns invalid JSON
# Solution: Add validation and retry logic

class SafeObjectiveGenerator(dspy.Module):
    def __init__(self, max_retries: int = 3):
        self.generator = TypedPredictor(ObjectiveSignature)
        self.max_retries = max_retries

    def forward(self, topic: str, level: str):
        for attempt in range(self.max_retries):
            try:
                result = self.generator(topic=topic, level=level)

                # Validate result structure
                if hasattr(result, 'verb') and hasattr(result, 'objective'):
                    if result.verb and result.objective:
                        return result

                print(f"⚠️  Invalid result format, retrying (attempt {attempt + 1})")

            except Exception as e:
                print(f"⚠️  Error generating objective: {e}, retrying (attempt {attempt + 1})")

        raise RuntimeError(f"Failed to generate valid objective after {self.max_retries} attempts")
```

#### Issue 2: Poor Quality Outputs
```python
# Problem: Generated objectives are not educationally sound
# Solution: Use few-shot learning and examples

class HighQualityObjectiveGenerator(dspy.Module):
    def __init__(self):
        self.generator = TypedPredictor(ObjectiveSignature)
        self.examples = [
            dspy.Example(
                topic="Introduction to Python",
                level="remember",
                verb="identify",
                objective="Identify the basic syntax and structure of Python programs"
            ),
            dspy.Example(
                topic="Python Variables",
                level="understand",
                verb="explain",
                objective="Explain the difference between variables, data types, and operators in Python"
            ),
            # Add more high-quality examples...
        ]

    def forward(self, topic: str, level: str):
        # Use context learning with examples
        with dspy.context(lm=dspy.settings.lm):
            # Set up few-shot examples
            dspy.settings.lm.update_config(
                few_shot_examples=self.examples,
                few_shot_mode="manual"
            )

            return self.generator(topic=topic, level=level)
```

---

## 📊 Performance Monitoring

### Example 9: DSPy Performance Tracking

```python
import time
from dataclasses import dataclass
from typing import List

@dataclass
class DSPyMetrics:
    """Track DSPy performance metrics."""

    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    total_time_ms: int = 0
    cache_hits: int = 0
    average_response_time_ms: float = 0.0

class TrackedObjectiveGenerator(dspy.Module):
    def __init__(self):
        self.generator = TypedPredictor(ObjectiveSignature)
        self.metrics = DSPyMetrics()
        self.cache = {}

    def forward(self, topic: str, level: str):
        start_time = time.time()
        self.metrics.total_requests += 1

        try:
            # Check cache first
            cache_key = f"{topic}_{level}"
            if cache_key in self.cache:
                self.metrics.cache_hits += 1
                result = self.cache[cache_key]
            else:
                # Generate new objective
                result = self.generator(topic=topic, level=level)
                self.cache[cache_key] = result

            self.metrics.successful_requests += 1
            response_time = (time.time() - start_time) * 1000
            self.metrics.total_time_ms += response_time

            return result

        except Exception as e:
            self.metrics.failed_requests += 1
            print(f"❌ DSPy generation failed: {e}")
            raise

    def get_metrics(self) -> DSPyMetrics:
        """Calculate and return current metrics."""
        self.metrics.average_response_time_ms = (
            self.metrics.total_time_ms / self.metrics.total_requests
            if self.metrics.total_requests > 0 else 0
        )
        return self.metrics
```

---

## 🎯 Next Steps

### Further DSPy Learning
1. **Explore Optimizers**: Try different teleprompters
2. **Experiment with Metrics**: Create custom evaluation metrics
3. **Build Complex Pipelines**: Chain multiple DSPy modules
4. **Optimize for Performance**: Fine-tune caching and batch processing

### Integration with Open-Instruct
1. **Start Simple**: Begin with basic TypedPredictor usage
2. **Add Validation**: Implement Bloom's Taxonomy validation
3. **Optimize Performance**: Use caching and batching
4. **Monitor Quality**: Track generation success rates

---

**Happy DSPy coding! 🚀**