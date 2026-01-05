"""
Unit tests for error handling and retry logic.

Tests the error_handlers module including:
- Circuit breaker pattern
- Exponential backoff retry
- Timeout wrapper
- Error response creation
"""

import time
import unittest
from datetime import datetime

from src.core.error_handlers import (
    CircuitBreaker,
    CircuitBreakerOpenError,
    CircuitState,
    GenerationTimeoutError,
    MaxRetriesExceededError,
    OllamaUnavailableError,
    check_ollama_health,
    create_circuit_breaker_open_error,
    create_generation_failed_error,
    create_generation_timeout_error,
    create_service_unavailable_error,
    create_validation_error,
    get_circuit_breaker,
    retry_with_exponential_backoff,
    timeout_wrapper,
)


class TestCircuitBreaker(unittest.TestCase):
    """Test circuit breaker pattern implementation."""

    def setUp(self):
        """Set up test fixtures."""
        # Create a fresh circuit breaker for each test
        self.breaker = CircuitBreaker(
            failure_threshold=3,  # Open after 3 failures
            timeout_seconds=5,    # Wait 5s before reset
            half_open_attempts=2  # Need 2 successes to close
        )

    def test_closed_state_initially(self):
        """Test that circuit breaker starts in CLOSED state."""
        self.assertEqual(self.breaker.state, CircuitState.CLOSED)
        self.assertEqual(self.breaker.failures, 0)

    def test_opens_after_threshold_failures(self):
        """Test that circuit opens after threshold failures."""
        def failing_function():
            raise ValueError("Test failure")

        # Trigger failures up to threshold
        for _ in range(self.breaker.failure_threshold):
            with self.assertRaises(ValueError):
                self.breaker.call(failing_function)

        # Circuit should now be open
        self.assertEqual(self.breaker.state, CircuitState.OPEN)
        self.assertEqual(self.breaker.failures, 3)

    def test_opens_circuit_immediately(self):
        """Test that open circuit raises error immediately."""
        def failing_function():
            raise ValueError("Test failure")

        # Trigger failures to open circuit
        for _ in range(self.breaker.failure_threshold):
            try:
                self.breaker.call(failing_function)
            except ValueError:
                pass

        # Next call should raise CircuitBreakerOpenError immediately
        with self.assertRaises(CircuitBreakerOpenError):
            self.breaker.call(failing_function)

    def test_resets_on_success(self):
        """Test that successes reset failure count."""
        def success_function():
            return "success"

        # Trigger some failures
        for i in range(self.breaker.failure_threshold - 1):
            try:
                self.breaker.call(lambda: (_ for _ in ()).throw(ValueError("Test")))
            except ValueError:
                pass

        # Circuit should still be closed
        self.assertEqual(self.breaker.state, CircuitState.CLOSED)

        # Success resets failures
        result = self.breaker.call(success_function)
        self.assertEqual(result, "success")
        self.assertEqual(self.breaker.failures, 0)

    def test_half_open_to_closed(self):
        """Test transition from HALF_OPEN to CLOSED."""
        # Open the circuit first
        for _ in range(self.breaker.failure_threshold):
            try:
                self.breaker.call(lambda: (_ for _ in ()).throw(ValueError("Test")))
            except ValueError:
                pass

        self.assertEqual(self.breaker.state, CircuitState.OPEN)

        # Manually transition to HALF_OPEN (simulating timeout)
        self.breaker.state = CircuitState.HALF_OPEN
        self.breaker.half_open_success_count = 0

        def success_function():
            return "success"

        # First success
        self.breaker.call(success_function)
        self.assertEqual(self.breaker.state, CircuitState.HALF_OPEN)
        self.assertEqual(self.breaker.half_open_success_count, 1)

        # Second success should close circuit
        self.breaker.call(success_function)
        self.assertEqual(self.breaker.state, CircuitState.CLOSED)
        self.assertEqual(self.breaker.failures, 0)
        self.assertEqual(self.breaker.half_open_success_count, 0)


class TestRetryWithExponentialBackoff(unittest.TestCase):
    """Test exponential backoff retry decorator."""

    def test_success_on_first_attempt(self):
        """Test function that succeeds immediately."""
        @retry_with_exponential_backoff(max_attempts=3, base_delay=0.01)
        def success_function():
            return "success"

        result = success_function()
        self.assertEqual(result, "success")

    def test_retry_then_success(self):
        """Test function that fails then succeeds."""
        call_count = 0

        @retry_with_exponential_backoff(max_attempts=3, base_delay=0.01)
        def flaky_function():
            nonlocal call_count
            call_count += 1
            if call_count < 2:
                raise ValueError("Temporary failure")
            return "success"

        result = flaky_function()
        self.assertEqual(result, "success")
        self.assertEqual(call_count, 2)

    def test_max_retries_exceeded(self):
        """Test that MaxRetriesExceededError is raised after all attempts."""
        @retry_with_exponential_backoff(max_attempts=3, base_delay=0.01)
        def always_failing_function():
            raise ValueError("Permanent failure")

        with self.assertRaises(MaxRetriesExceededError):
            always_failing_function()

    def test_exponential_backoff_timing(self):
        """Test that delays increase exponentially."""
        call_times = []

        @retry_with_exponential_backoff(max_attempts=4, base_delay=0.05, max_delay=0.5)
        def failing_function():
            call_times.append(time.time())
            raise ValueError("Test failure")

        with self.assertRaises(MaxRetriesExceededError):
            failing_function()

        # Check that delays increase
        if len(call_times) >= 3:
            delay1 = call_times[1] - call_times[0]
            delay2 = call_times[2] - call_times[1]
            # Second delay should be roughly double the first
            self.assertGreater(delay2, delay1 * 1.5)


class TestTimeoutWrapper(unittest.TestCase):
    """Test timeout wrapper decorator."""

    def test_success_before_timeout(self):
        """Test function that completes before timeout."""
        @timeout_wrapper(timeout_seconds=1)
        def quick_function():
            return "quick"

        result = quick_function()
        self.assertEqual(result, "quick")

    def test_timeout_exception(self):
        """Test that timeout raises GenerationTimeoutError."""
        @timeout_wrapper(timeout_seconds=0.1)
        def slow_function():
            time.sleep(1)
            return "slow"

        with self.assertRaises(GenerationTimeoutError):
            slow_function()


class TestErrorCreation(unittest.TestCase):
    """Test error response creation functions."""

    def test_create_validation_error(self):
        """Test validation error creation."""
        error = create_validation_error(
            field="topic",
            value="",
            constraint="Topic must be between 1 and 200 characters",
            suggestion="Enter a descriptive topic for your course"
        )

        error_dict = error.to_dict()
        self.assertEqual(error_dict["code"], "VALIDATION_ERROR")
        self.assertEqual(error_dict["message"], "Invalid input data")
        self.assertEqual(error_dict["details"]["field"], "topic")
        self.assertIn("suggestion", error_dict["details"])

    def test_create_service_unavailable_error(self):
        """Test service unavailable error creation."""
        error = create_service_unavailable_error(
            service="Ollama",
            cached_content_available=False
        )

        error_dict = error.to_dict()
        self.assertEqual(error_dict["code"], "SERVICE_UNAVAILABLE")
        self.assertIn("Ollama", error_dict["message"])
        self.assertEqual(error_dict["details"]["cached_content_available"], False)

    def test_create_generation_timeout_error(self):
        """Test generation timeout error creation."""
        error = create_generation_timeout_error(
            timeout_seconds=60,
            suggestion="Try a simpler topic"
        )

        error_dict = error.to_dict()
        self.assertEqual(error_dict["code"], "GENERATION_TIMEOUT")
        self.assertIn("60", error_dict["message"])
        self.assertEqual(error_dict["details"]["timeout_seconds"], 60)

    def test_create_generation_failed_error(self):
        """Test generation failed error creation."""
        error = create_generation_failed_error(
            attempts=3,
            errors=["Invalid JSON", "Schema validation failed", "Invalid JSON"],
            raw_output="Some partial output..."
        )

        error_dict = error.to_dict()
        self.assertEqual(error_dict["code"], "GENERATION_FAILED")
        self.assertEqual(error_dict["details"]["attempts"], 3)
        self.assertIn("suggestion", error_dict["details"])
        self.assertIn("raw_output", error_dict["details"])

    def test_create_circuit_breaker_open_error(self):
        """Test circuit breaker open error creation."""
        error = create_circuit_breaker_open_error(
            remaining_timeout=45
        )

        error_dict = error.to_dict()
        self.assertEqual(error_dict["code"], "CIRCUIT_BREAKER_OPEN")
        self.assertEqual(error_dict["details"]["retry_after_seconds"], 45)
        self.assertIn("cascading failures", error_dict["details"]["reason"])


class TestOllamaHealthCheck(unittest.TestCase):
    """Test Ollama health check function."""

    def test_health_check_returns_boolean(self):
        """Test that health check returns boolean."""
        result = check_ollama_health()
        self.assertIsInstance(result, bool)
        # Will likely be False in test environment unless Ollama is running


if __name__ == "__main__":
    unittest.main()
