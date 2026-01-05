# Error Scenarios & Handling Guide

**Audience**: Junior Developers
**Purpose**: Complete guide to error handling for Open-Instruct
**Philosophy**: "Fail gracefully, always provide a path forward"

---

## Table of Contents
1. [Error Handling Philosophy](#error-handling-philosophy)
2. [Error Categories](#error-categories)
3. [Common Error Scenarios](#common-error-scenarios)
4. [Retry Strategies](#retry-strategies)
5. [Error Response Formats](#error-response-formats)
6. [Logging & Monitoring](#logging--monitoring)
7. [Circuit Breaker Pattern](#circuit-breaker-pattern)
8. [Recovery Procedures](#recovery-procedures)

---

## Error Handling Philosophy

### Core Principles

1. **Never Crash Silently**: All errors must be logged with context
2. **User-Facing Messages**: Technical details hidden, actionable advice shown
3. **Graceful Degradation**: System continues working at reduced capacity if possible
4. **Retry Smartly**: Automatic retry for transient failures, fast fail for permanent errors
5. **Preserve Data**: Never lose user data due to errors

### Error Decision Tree

```
Error Occurs
    │
    ├─► Is it transient (network, timeout)?
    │   └─► YES → Retry (exponential backoff)
    │             └─► After 3 attempts → Return cached result OR graceful error
    │
    ├─► Is it validation error (bad input)?
    │   └─► YES → Return specific validation message (no retry)
    │
    ├─► Is it LLM hallucination (invalid JSON)?
    │   └─► YES → Retry with stronger constraints (max 3 attempts)
    │             └─► After 3 attempts → Return partial result OR error
    │
    └─► Is it system error (Ollama down)?
        └─► YES → Return cached results if available
                  └─► Clear error message if no cache
```

---

## Error Categories

### Category 1: Transient Errors

**Definition**: Temporary failures that resolve on retry

| Error Type | Retry Strategy | Max Attempts |
|------------|----------------|--------------|
| Network timeout to Ollama | Exponential backoff (1s, 2s, 4s) | 3 |
| Ollama temporarily unavailable | Wait 30s, retry | 2 |
| LLM returns invalid JSON (rare) | Reprompt with stronger constraints | 3 |
| Database lock | Wait 100ms, retry | 5 |

### Category 2: Validation Errors

**Definition**: Invalid input from user

| Error Type | Retry Strategy | User Action |
|------------|----------------|-------------|
| Topic too long/short | No retry | Fix input |
| Invalid Bloom's level | No retry | Use dropdown |
| Malformed JSON request | No retry | Fix JSON syntax |

### Category 3: System Errors

**Definition**: Service unavailable

| Error Type | Fallback Strategy |
|------------|-------------------|
| Ollama not running | Show cached courses |
| Disk full | Read-only mode, error message |
| Out of memory | Stop accepting new requests |

### Category 4: LLM Hallucinations

**Definition**: LLM produces invalid/malformed output

| Error Type | Retry Strategy |
|------------|----------------|
| Invalid JSON | Reprompt with example |
| Wrong Bloom's verbs | Auto-replace with valid verbs |
| Too few objectives | Reprompt with explicit count |
| Duplicate IDs | Auto-fix in post-processing |

---

## Common Error Scenarios

### Scenario 1: Ollama Not Running

**Symptoms**:
- Connection refused to `localhost:11434`
- All LLM calls timeout after 30s

**Detection**:
```python
def check_ollama_health() -> bool:
    """Check if Ollama is running."""
    import requests
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=2)
        return response.status_code == 200
    except (requests.ConnectionError, requests.Timeout):
        return False
```

**Handling**:
```python
# src/core/dspy_client.py

class OllamaUnavailableError(Exception):
    """Raised when Ollama is not running."""

def generate_with_fallback(topic: str):
    """Generate objectives with fallback options."""

    # Check Ollama health
    if not check_ollama_health():
        # Try to return cached result
        cached = get_cached_result(topic)
        if cached:
            logger.warning("Ollama down, returning cached result")
            return {
                "success": True,
                "data": cached,
                "meta": {
                    "cache_hit": True,
                    "ollama_available": False,
                    "message": "Ollama service unavailable. Showing cached content."
                }
            }

        # No cache available
        raise OllamaUnavailableError(
            "Ollama service not running. Start it with 'ollama serve' and try again."
        )

    # Ollama is available, proceed normally
    return generate_objectives(topic)
```

**User-Facing Error**:
```json
{
  "success": false,
  "error": {
    "code": "SERVICE_UNAVAILABLE",
    "message": "The AI learning model service is currently unavailable.",
    "details": {
      "reason": "Ollama is not running",
      "action": "Start Ollama with 'ollama serve' or try again later",
      "cached_content_available": true
    }
  }
}
```

---

### Scenario 2: LLM Returns Invalid JSON

**Symptoms**:
- JSON parsing fails
- LLM adds markdown code blocks
- Trailing text after JSON

**Detection**:
```python
import json

def parse_llm_output(raw_output: str) -> dict:
    """Parse LLM output, handling common issues."""

    # Issue 1: Markdown code blocks
    if raw_output.strip().startswith('```'):
        # Extract JSON from code block
        lines = raw_output.split('\n')
        json_lines = []
        in_code_block = False
        for line in lines:
            if line.startswith('```'):
                in_code_block = not in_code_block
                continue
            if in_code_block:
                json_lines.append(line)
        raw_output = '\n'.join(json_lines)

    # Issue 2: Trailing text
    # Find first { and last }
    first_brace = raw_output.find('{')
    last_brace = raw_output.rfind('}')

    if first_brace != -1 and last_brace != -1:
        raw_output = raw_output[first_brace:last_brace + 1]

    # Parse JSON
    try:
        return json.loads(raw_output)
    except json.JSONDecodeError as e:
        raise InvalidJSONError(f"Failed to parse JSON: {e}")
```

**Handling with Retry**:
```python
# src/modules/architect.py

def generate_objectives_with_retry(topic: str, max_attempts: int = 3):
    """Generate objectives with intelligent retry logic."""

    for attempt in range(max_attempts):
        try:
            # Call LLM
            raw_output = call_llm(topic)

            # Parse output
            parsed = parse_llm_output(raw_output)

            # Validate
            course = CourseStructure(**parsed)
            validate_objectives(course)

            # Success!
            log_generation_attempt(request_id, success=True, attempt=attempt+1)
            return course

        except json.JSONDecodeError as e:
            logger.warning(f"Attempt {attempt+1}: Invalid JSON - {e}")

            if attempt < max_attempts - 1:
                # Retry with stronger constraints
                logger.info("Retrying with stronger JSON enforcement...")
                continue
            else:
                # Final attempt failed
                log_generation_attempt(request_id, success=False, error=str(e))
                raise InvalidJSONError(
                    f"Failed to generate valid JSON after {max_attempts} attempts. "
                    f"Try simplifying your topic or use a different model."
                )

        except ValidationError as e:
            # Schema validation failed
            logger.warning(f"Attempt {attempt+1}: Schema validation failed - {e}")

            if attempt < max_attempts - 1:
                continue
            else:
                raise ValidationError(
                    f"LLM output doesn't match expected format: {e}"
                )
```

---

### Scenario 3: LLM Uses Invalid Bloom's Verbs

**Symptoms**:
- Verb "create" used for Remember level
- Verb "define" used for Create level

**Auto-Correction**:
```python
# src/modules/validators.py

def validate_and_fix_verbs(course: CourseStructure) -> CourseStructure:
    """Validate and fix invalid Bloom's verbs."""

    fixes_made = []

    for obj in course.objectives:
        if not BloomsTaxonomy.validate_verb(obj.verb, obj.level):
            # Invalid verb detected
            logger.warning(
                f"Invalid verb '{obj.verb}' for {obj.level} level"
            )

            # Get correct verb
            original_verb = obj.verb
            obj.verb = BloomsTaxonomy.get_random_verb(obj.level)

            logger.info(f"Replaced '{original_verb}' with '{obj.verb}'")
            fixes_made.append({
                "objective_id": obj.id,
                "original": original_verb,
                "replacement": obj.verb
            })

    if fixes_made:
        logger.info(f"Fixed {len(fixes_made)} invalid verbs")

    return course
```

---

### Scenario 4: Generation Timeout

**Symptoms**:
- LLM takes > 60 seconds to respond
- Request hangs indefinitely

**Timeout Handling**:
```python
# src/modules/architect.py

import signal
from contextlib import contextmanager

class TimeoutError(Exception):
    """Raised when generation times out."""

@contextmanager
def timeout_context(seconds: int):
    """Timeout context manager."""

    def timeout_handler(signum, frame):
        raise TimeoutError(f"Operation timed out after {seconds} seconds")

    # Set alarm
    old_handler = signal.signal(signal.SIGALRM, timeout_handler)
    signal.alarm(seconds)

    try:
        yield
    finally:
        signal.alarm(0)  # Cancel alarm
        signal.signal(signal.SIGALRM, old_handler)  # Restore handler

def generate_with_timeout(topic: str, timeout_seconds: int = 60):
    """Generate objectives with timeout."""

    try:
        with timeout_context(timeout_seconds):
            return generate_objectives(topic)

    except TimeoutError:
        logger.error(f"Generation timed out after {timeout_seconds}s for topic: {topic}")

        # Check for partial results
        partial = get_partial_results(topic)

        if partial:
            return {
                "success": True,
                "data": partial,
                "meta": {
                    "partial_results": True,
                    "message": "Generation timed out. Showing partial results."
                }
            }

        raise TimeoutError(
            f"Generation timed out after {timeout_seconds} seconds. "
            f"Try a simpler topic or ensure Ollama has enough resources."
        )
```

---

### Scenario 5: Database Locked

**Symptoms**:
- `sqlite3.OperationalError: database is locked`
- Concurrent write attempts

**Handling**:
```python
import time
import sqlite3

from sqlite3 import OperationalError

def execute_with_retry(sql: str, params: tuple, max_retries: int = 5):
    """Execute SQL with retry for database locks."""

    for attempt in range(max_retries):
        try:
            conn = sqlite3.connect(DB_PATH, timeout=10.0)
            cursor = conn.cursor()
            cursor.execute(sql, params)
            conn.commit()
            conn.close()
            return

        except OperationalError as e:
            if "locked" in str(e).lower() and attempt < max_retries - 1:
                # Wait and retry
                wait_time = 0.1 * (2 ** attempt)  # Exponential backoff
                logger.warning(f"Database locked, retrying in {wait_time}s...")
                time.sleep(wait_time)
                continue
            else:
                raise

    raise DatabaseError(f"Failed after {max_retries} attempts: {e}")
```

---

### Scenario 6: Out of Memory

**Symptoms**:
- Ollama crashes during generation
- System becomes unresponsive

**Monitoring**:
```python
import psutil

def check_memory_usage() -> dict:
    """Check system memory usage."""

    memory = psutil.virtual_memory()

    return {
        "total_gb": memory.total / (1024**3),
        "available_gb": memory.available / (1024**3),
        "used_percent": memory.percent,
        "is_low": memory.available < (2 * 1024**3)  # Less than 2GB
    }

def safe_to_generate() -> bool:
    """Check if system has enough memory to generate."""

    memory = check_memory_usage()

    if memory["is_low"]:
        logger.warning(f"Low memory: {memory['available_gb']:.2f}GB available")
        return False

    return True
```

**Handling**:
```python
def generate_with_memory_check(topic: str):
    """Generate only if sufficient memory available."""

    if not safe_to_generate():
        raise MemoryError(
            "Insufficient memory to generate content. "
            "Close other applications or try a smaller model."
        )

    return generate_objectives(topic)
```

---

## Retry Strategies

### Strategy 1: Exponential Backoff

```python
import time

def retry_with_backoff(func, max_attempts: int = 3):
    """Retry function with exponential backoff."""

    for attempt in range(max_attempts):
        try:
            return func()

        except TransientError as e:
            if attempt == max_attempts - 1:
                raise

            # Exponential backoff: 1s, 2s, 4s
            wait_time = 2 ** attempt
            logger.warning(f"Attempt {attempt+1} failed: {e}, retrying in {wait_time}s...")
            time.sleep(wait_time)

    raise MaxRetriesExceededError(f"Failed after {max_attempts} attempts")
```

### Strategy 2: Jitter (Randomized Delay)

Prevents thundering herd problem:

```python
import random
import time

def retry_with_jitter(func, max_attempts: int = 3):
    """Retry with randomized jitter."""

    for attempt in range(max_attempts):
        try:
            return func()

        except TransientError as e:
            if attempt == max_attempts - 1:
                raise

            # Random jitter: 0.5s - 2.0s
            wait_time = random.uniform(0.5, 2.0)
            time.sleep(wait_time)

    raise MaxRetriesExceededError()
```

### Strategy 3: Constraint Strengthening

For LLM hallucinations:

```python
def generate_with_strengthening(topic: str):
    """Generate with stronger constraints on each retry."""

    prompts = [
        # Attempt 1: Normal prompt
        build_prompt(topic, strictness="normal"),

        # Attempt 2: Add JSON example
        build_prompt(topic, strictness="high", include_example=True),

        # Attempt 3: Emphasize JSON only
        build_prompt(topic, strictness="extreme", json_only=True)
    ]

    for attempt, prompt in enumerate(prompts):
        try:
            result = call_llm(prompt)
            return parse_and_validate(result)

        except InvalidJSONError:
            if attempt < len(prompts) - 1:
                logger.info(f"Attempt {attempt+1} failed, strengthening constraints...")
                continue
            else:
                raise
```

---

## Error Response Formats

### Format 1: Validation Error

```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid input data",
    "details": {
      "field": "topic",
      "value": "",
      "constraint": "Topic must be between 1 and 200 characters",
      "suggestion": "Enter a descriptive topic for your course"
    }
  }
}
```

### Format 2: Service Unavailable

```json
{
  "success": false,
  "error": {
    "code": "SERVICE_UNAVAILABLE",
    "message": "AI service temporarily unavailable",
    "details": {
      "service": "Ollama",
      "status": "down",
      "retry_after_seconds": 30,
      "cached_content_available": true
    }
  }
}
```

### Format 3: Generation Failed

```json
{
  "success": false,
  "error": {
    "code": "GENERATION_FAILED",
    "message": "Failed to generate valid content after 3 attempts",
    "details": {
      "attempts": 3,
      "errors": [
        "Invalid JSON (attempt 1)",
        "Schema validation failed (attempt 2)",
        "Invalid JSON (attempt 3)"
      ],
      "raw_output": "Last failed LLM output...",
      "suggestion": "Try simplifying your topic or use a larger model"
    }
  }
}
```

### Format 4: Partial Success

```json
{
  "success": true,
  "data": {
    "course": { ... },
    "objectives": [ ... ]
  },
  "meta": {
    "partial_results": true,
    "warnings": [
      "Only 4 objectives generated (requested 6)",
      "1 objective had invalid verb and was auto-corrected"
    ],
    "quality_score": 0.75
  }
}
```

---

## Logging & Monitoring

### Structured Logging

```python
# src/utils/logging.py

import structlog
import logging

def configure_logging():
    """Configure structured logging."""

    structlog.configure(
        processors=[
            structlog.stdlib.add_log_level,
            structlog.stdlib.add_logger_name,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.JSONRenderer()
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )

# Usage
logger = structlog.get_logger()

logger.error(
    "generation_failed",
    request_id="req_abc123",
    topic="Python functions",
    attempts=3,
    error="Invalid JSON",
    duration_ms=15000
)
```

### Log Levels

| Level | When to Use | Example |
|-------|--------------|---------|
| DEBUG | Detailed tracing | "Prompt sent to LLM: {prompt}" |
| INFO | Normal operations | "Generated 6 objectives for topic: Python" |
| WARNING | Recoverable issues | "Invalid verb 'create' for Remember level, auto-corrected" |
| ERROR | Errors handled | "Failed to parse JSON after 3 attempts" |
| CRITICAL | System failures | "Ollama service not responding" |

### Error Metrics to Track

```python
# src/utils/metrics.py

from collections import defaultdict
from datetime import datetime, timedelta

class ErrorMetrics:
    """Track error rates and patterns."""

    def __init__(self):
        self.errors = defaultdict(int)
        self.errors_last_hour = defaultdict(int)

    def record_error(self, error_code: str):
        """Record an error occurrence."""
        self.errors[error_code] += 1
        self.errors_last_hour[error_code] += 1

    def get_summary(self) -> dict:
        """Get error summary for last hour."""

        total = sum(self.errors_last_hour.values())

        return {
            "total_errors_last_hour": total,
            "error_breakdown": dict(self.errors_last_hour),
            "most_common": max(
                self.errors_last_hour.items(),
                key=lambda x: x[1]
            )[0] if self.errors_last_hour else None
        }

    def reset_hourly_metrics(self):
        """Reset hourly metrics (call every hour)."""
        self.errors_last_hour.clear()
```

---

## Circuit Breaker Pattern

### Purpose

Prevent cascading failures when Ollama is struggling

### Implementation

```python
# src/utils/circuit_breaker.py

from enum import Enum
from datetime import datetime, timedelta

class CircuitState(Enum):
    CLOSED = "closed"      # Normal operation
    OPEN = "open"          # Failing, stop requests
    HALF_OPEN = "half_open"  # Testing if recovered

class CircuitBreaker:
    """Circuit breaker for LLM calls."""

    def __init__(
        self,
        failure_threshold: int = 5,
        timeout_seconds: int = 60,
        half_open_attempts: int = 3
    ):
        self.failure_threshold = failure_threshold
        self.timeout_seconds = timeout_seconds
        self.half_open_attempts = half_open_attempts

        self.state = CircuitState.CLOSED
        self.failures = 0
        self.last_failure_time = None
        self.half_open_success_count = 0

    def call(self, func, *args, **kwargs):
        """Execute function with circuit breaker protection."""

        # Check if circuit is open
        if self.state == CircuitState.OPEN:
            if self._should_attempt_reset():
                self.state = CircuitState.HALF_OPEN
                logger.info("Circuit breaker: HALF_OPEN (testing recovery)")
            else:
                raise CircuitBreakerOpenError(
                    f"Circuit breaker is OPEN. Too many failures. "
                    f"Retry after {self._get_remaining_timeout()}s."
                )

        try:
            # Execute the function
            result = func(*args, **kwargs)

            # Success!
            self._on_success()

            return result

        except Exception as e:
            # Failure!
            self._on_failure()

            # Re-raise
            raise

    def _on_success(self):
        """Handle successful call."""

        if self.state == CircuitState.HALF_OPEN:
            self.half_open_success_count += 1

            # Close circuit if enough successes
            if self.half_open_success_count >= self.half_open_attempts:
                self.state = CircuitState.CLOSED
                self.failures = 0
                self.half_open_success_count = 0
                logger.info("Circuit breaker: CLOSED (recovered)")
        else:
            # Reset failures on success
            self.failures = 0

    def _on_failure(self):
        """Handle failed call."""

        self.failures += 1
        self.last_failure_time = datetime.now()

        if self.failures >= self.failure_threshold:
            self.state = CircuitState.OPEN
            logger.error(
                f"Circuit breaker: OPEN (too many failures: {self.failures})"
            )

    def _should_attempt_reset(self) -> bool:
        """Check if enough time has passed to attempt reset."""
        if not self.last_failure_time:
            return True

        elapsed = datetime.now() - self.last_failure_time
        return elapsed.total_seconds() >= self.timeout_seconds

    def _get_remaining_timeout(self) -> int:
        """Get remaining seconds before circuit can close."""

        if not self.last_failure_time:
            return 0

        elapsed = datetime.now() - self.last_failure_time
        remaining = self.timeout_seconds - elapsed.total_seconds()
        return max(0, int(remaining))

# Usage
circuit_breaker = CircuitBreaker(
    failure_threshold=5,   # Open after 5 failures
    timeout_seconds=60,    # Try again after 60s
    half_open_attempts=3   # Need 3 successes to close
)

def safe_generate_objectives(topic: str):
    """Generate with circuit breaker protection."""

    return circuit_breaker.call(
        generate_objectives,
        topic
    )
```

---

## Recovery Procedures

### Recovery 1: Ollama Crashed

**Symptoms**: Connection refused, timeouts

**Recovery Steps**:
```bash
# 1. Check if Ollama process is running
ps aux | grep ollama

# 2. Restart Ollama
ollama serve

# 3. Verify it's working
ollama list

# 4. Test generation
python -m src.modules.architect "Test topic"
```

### Recovery 2: Database Corrupted

**Symptoms**: SQLite errors, unable to read/write

**Recovery Steps**:
```bash
# 1. Check database integrity
sqlite3 backend/data/open_instruct.db "PRAGMA integrity_check;"

# 2. Dump data
sqlite3 backend/data/open_instruct.db .dump > backup.sql

# 3. Create new database
rm backend/data/open_instruct.db
sqlite3 backend/data/open_instruct.db < backup.sql

# 4. Verify
sqlite3 backend/data/open_instruct.db "SELECT COUNT(*) FROM courses;"
```

### Recovery 3: Out of Disk Space

**Symptoms**: Write errors, database locked

**Recovery Steps**:
```bash
# 1. Check disk usage
df -h

# 2. Clean up old logs
find backend/logs/ -name "*.log" -mtime +7 -delete

# 3. Clean up old cache entries (via Python)
python -c "from src.db import cleanup; cleanup.delete_expired_cache()"

# 4. Vacuum database
sqlite3 backend/data/open_instruct.db "VACUUM;"
```

### Recovery 4: Memory Leak

**Symptoms**: Generation gets slower over time, system sluggish

**Recovery Steps**:
```bash
# 1. Restart Ollama (clears memory)
pkill ollama
ollama serve

# 2. Restart application
pkill -f "uvicorn src.api"
uvicorn src.api:app

# 3. Monitor memory
watch -n 5 'ps aux | grep ollama'
```

---

## Quick Reference: Error Codes

| Code | HTTP | Description | Retry? |
|------|------|-------------|--------|
| `VALIDATION_ERROR` | 400 | Invalid input | No |
| `INVALID_JSON` | 422 | LLM output not valid JSON | Yes (3x) |
| `INVALID_VERB` | 422 | Wrong Bloom's verb | No (auto-fix) |
| `SERVICE_UNAVAILABLE` | 503 | Ollama not running | No |
| `TIMEOUT` | 504 | Generation too slow | No |
| `DATABASE_LOCKED` | 500 | SQLite locked | Yes (5x) |
| `OUT_OF_MEMORY` | 500 | System OOM | No |
| `CIRCUIT_BREAKER_OPEN` | 503 | Too many failures | No |

---

## Next Steps

1. **Implement error handlers** for each scenario
2. **Add structured logging** throughout codebase
3. **Set up monitoring** dashboard
4. **Create runbook** for common issues
5. **Test error scenarios** regularly

Remember: **Good error handling is invisible**. Users should rarely see errors, and when they do, the path forward should be clear.
