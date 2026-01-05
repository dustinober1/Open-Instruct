"""
Error handling and retry logic for Open-Instruct.

This module provides comprehensive error handling including:
- Exponential backoff retry for transient failures (max 3 retries)
- Timeout protection for LLM calls (60 second kill switch)
- Circuit breaker pattern for Ollama failures (open circuit after 5 consecutive failures)
- Graceful degradation when Ollama is down (return cached results if available)
- Structured error responses with user-friendly messages
"""

import functools
import logging
import time
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Callable, Dict, Optional, TypeVar

logger = logging.getLogger(__name__)

T = TypeVar('T')


class CircuitState(Enum):
    """Circuit breaker states."""
    CLOSED = "closed"      # Normal operation
    OPEN = "open"          # Failing, stop requests
    HALF_OPEN = "half_open"  # Testing if recovered


class CircuitBreakerOpenError(Exception):
    """Raised when circuit breaker is open."""
    pass


class GenerationTimeoutError(Exception):
    """Raised when generation times out."""
    pass


class OllamaUnavailableError(Exception):
    """Raised when Ollama is not running."""
    pass


class MaxRetriesExceededError(Exception):
    """Raised when max retries exceeded."""
    pass


class CircuitBreaker:
    """Circuit breaker for LLM calls.

    Prevents cascading failures when Ollama is struggling by opening the circuit
    after a threshold of consecutive failures and allowing it to reset after a timeout.

    Attributes:
        failure_threshold: Number of consecutive failures before opening circuit (default: 5)
        timeout_seconds: Seconds to wait before attempting to close circuit (default: 60)
        half_open_attempts: Number of successful attempts needed to close circuit (default: 3)
    """

    def __init__(
        self,
        failure_threshold: int = 5,
        timeout_seconds: int = 60,
        half_open_attempts: int = 3,
    ):
        """Initialize circuit breaker.

        Args:
            failure_threshold: Open circuit after this many consecutive failures
            timeout_seconds: Wait this long before attempting reset
            half_open_attempts: Need this many successes to close circuit
        """
        self.failure_threshold = failure_threshold
        self.timeout_seconds = timeout_seconds
        self.half_open_attempts = half_open_attempts

        self.state = CircuitState.CLOSED
        self.failures = 0
        self.last_failure_time: Optional[datetime] = None
        self.half_open_success_count = 0

    def call(self, func: Callable[..., T], *args: Any, **kwargs: Any) -> T:
        """Execute function with circuit breaker protection.

        Args:
            func: Function to execute
            *args: Positional arguments for func
            **kwargs: Keyword arguments for func

        Returns:
            Result of func(*args, **kwargs)

        Raises:
            CircuitBreakerOpenError: If circuit is open and timeout not expired
        """
        # Check if circuit is open
        if self.state == CircuitState.OPEN:
            if self._should_attempt_reset():
                self.state = CircuitState.HALF_OPEN
                self.half_open_success_count = 0
                logger.info("Circuit breaker: HALF_OPEN (testing recovery)")
            else:
                remaining = self._get_remaining_timeout()
                raise CircuitBreakerOpenError(
                    f"Circuit breaker is OPEN. Too many failures. "
                    f"Retry after {remaining}s."
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

            # Re-raise the original exception
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
            # Reset failures on success in CLOSED state
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

    def reset(self):
        """Manually reset circuit breaker to CLOSED state."""
        self.state = CircuitState.CLOSED
        self.failures = 0
        self.last_failure_time = None
        self.half_open_success_count = 0
        logger.info("Circuit breaker: manually reset to CLOSED")


# Global circuit breaker instance
_ollama_circuit_breaker = CircuitBreaker(
    failure_threshold=5,
    timeout_seconds=60,
    half_open_attempts=3
)


def get_circuit_breaker() -> CircuitBreaker:
    """Get the global Ollama circuit breaker instance."""
    return _ollama_circuit_breaker


def retry_with_exponential_backoff(
    max_attempts: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 10.0,
    exceptions: tuple = (Exception,),
):
    """Decorator for retry with exponential backoff.

    Retries the decorated function with exponential backoff delay between attempts.
    Delay formula: min(base_delay * 2^attempt, max_delay)

    Args:
        max_attempts: Maximum number of retry attempts (default: 3)
        base_delay: Base delay in seconds before first retry (default: 1.0)
        max_delay: Maximum delay between retries in seconds (default: 10.0)
        exceptions: Tuple of exception types to catch and retry on

    Returns:
        Decorator function

    Example:
        @retry_with_exponential_backoff(max_attempts=3, base_delay=1.0)
        def generate_objectives(topic: str):
            # ... generation logic
            pass
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> T:
            last_exception = None

            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)

                except exceptions as e:
                    last_exception = e

                    if attempt < max_attempts - 1:
                        # Calculate delay with exponential backoff
                        delay = min(base_delay * (2 ** attempt), max_delay)

                        logger.warning(
                            f"Attempt {attempt + 1}/{max_attempts} failed for {func.__name__}: {e}. "
                            f"Retrying in {delay:.1f}s..."
                        )

                        time.sleep(delay)
                    else:
                        logger.error(
                            f"All {max_attempts} attempts failed for {func.__name__}: {e}"
                        )

            # All retries exhausted
            raise MaxRetriesExceededError(
                f"Failed after {max_attempts} attempts: {last_exception}"
            ) from last_exception

        return wrapper
    return decorator


def timeout_wrapper(timeout_seconds: int = 60):
    """Decorator to add timeout protection to function calls.

    Uses a separate thread to enforce timeout. If function execution exceeds
    the timeout, the thread is cancelled and GenerationTimeoutError is raised.

    Args:
        timeout_seconds: Maximum execution time in seconds (default: 60)

    Returns:
        Decorator function

    Example:
        @timeout_wrapper(timeout_seconds=60)
        def generate_objectives(topic: str):
            # ... generation logic that might hang
            pass
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> T:
            import concurrent.futures
            import threading

            # Use ThreadPoolExecutor to enforce timeout
            with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
                future = executor.submit(func, *args, **kwargs)

                try:
                    return future.result(timeout=timeout_seconds)

                except concurrent.futures.TimeoutError:
                    # Attempt to cancel the future
                    future.cancel()

                    logger.error(
                        f"Function {func.__name__} exceeded {timeout_seconds}s timeout"
                    )

                    raise GenerationTimeoutError(
                        f"Operation timed out after {timeout_seconds} seconds"
                    )

        return wrapper
    return decorator


class ErrorDetail:
    """Structured error detail for user-facing error responses."""

    def __init__(
        self,
        code: str,
        message: str,
        details: Optional[Dict[str, Any]] = None,
    ):
        """Initialize error detail.

        Args:
            code: Error code (e.g., "SERVICE_UNAVAILABLE", "VALIDATION_ERROR")
            message: User-friendly error message
            details: Additional error context and suggestions
        """
        self.code = code
        self.message = message
        self.details = details or {}

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "code": self.code,
            "message": self.message,
            "details": self.details,
        }


class ErrorResponse:
    """Structured error response for API errors."""

    def __init__(
        self,
        error: ErrorDetail,
        request_id: str,
    ):
        """Initialize error response.

        Args:
            error: ErrorDetail instance
            request_id: Unique request identifier
        """
        self.error = error
        self.request_id = request_id
        self.timestamp = datetime.utcnow()

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "success": False,
            "error": self.error.to_dict(),
            "meta": {
                "request_id": self.request_id,
                "timestamp": self.timestamp.isoformat(),
            },
        }


def create_validation_error(
    field: str,
    value: Any,
    constraint: str,
    suggestion: str,
) -> ErrorDetail:
    """Create a validation error detail.

    Args:
        field: Field name that failed validation
        value: Invalid value provided
        constraint: Description of constraint violated
        suggestion: Actionable suggestion for fixing

    Returns:
        ErrorDetail instance
    """
    return ErrorDetail(
        code="VALIDATION_ERROR",
        message="Invalid input data",
        details={
            "field": field,
            "value": str(value),
            "constraint": constraint,
            "suggestion": suggestion,
        },
    )


def create_service_unavailable_error(
    service: str,
    cached_content_available: bool = False,
) -> ErrorDetail:
    """Create a service unavailable error detail.

    Args:
        service: Service name (e.g., "Ollama")
        cached_content_available: Whether cached results are available

    Returns:
        ErrorDetail instance
    """
    details = {
        "service": service,
        "status": "down",
        "cached_content_available": cached_content_available,
    }

    if cached_content_available:
        details["action"] = "Showing cached content while service is unavailable"
    else:
        details["action"] = f"Start {service} and try again, or contact support"

    return ErrorDetail(
        code="SERVICE_UNAVAILABLE",
        message=f"{service} service temporarily unavailable",
        details=details,
    )


def create_generation_timeout_error(
    timeout_seconds: int,
    suggestion: str = "Try a simpler topic or ensure Ollama has enough resources",
) -> ErrorDetail:
    """Create a generation timeout error detail.

    Args:
        timeout_seconds: Timeout duration in seconds
        suggestion: Actionable suggestion

    Returns:
        ErrorDetail instance
    """
    return ErrorDetail(
        code="GENERATION_TIMEOUT",
        message=f"Generation exceeded {timeout_seconds} second timeout",
        details={
            "timeout_seconds": timeout_seconds,
            "suggestion": suggestion,
        },
    )


def create_generation_failed_error(
    attempts: int,
    errors: list,
    raw_output: Optional[str] = None,
) -> ErrorDetail:
    """Create a generation failed error detail.

    Args:
        attempts: Number of attempts made
        errors: List of error messages from each attempt
        raw_output: Raw LLM output from last failed attempt

    Returns:
        ErrorDetail instance
    """
    details = {
        "attempts": attempts,
        "errors": errors,
        "suggestion": "Try simplifying your topic or use a larger model",
    }

    if raw_output:
        # Truncate raw output if too long
        details["raw_output"] = raw_output[:500] + "..." if len(raw_output) > 500 else raw_output

    return ErrorDetail(
        code="GENERATION_FAILED",
        message=f"Failed to generate valid content after {attempts} attempts",
        details=details,
    )


def create_circuit_breaker_open_error(
    remaining_timeout: int,
) -> ErrorDetail:
    """Create a circuit breaker open error detail.

    Args:
        remaining_timeout: Seconds remaining before circuit can close

    Returns:
        ErrorDetail instance
    """
    return ErrorDetail(
        code="CIRCUIT_BREAKER_OPEN",
        message="Too many consecutive failures. Service temporarily blocked.",
        details={
            "retry_after_seconds": remaining_timeout,
            "reason": "Circuit breaker is open to prevent cascading failures",
            "suggestion": f"Wait {remaining_timeout}s before retrying, or check if Ollama is healthy",
        },
    )


def handle_ollama_error(
    error: Exception,
    request_id: str,
) -> ErrorResponse:
    """Convert Ollama-related exceptions to structured error responses.

    Args:
        error: Exception that occurred
        request_id: Request identifier

    Returns:
        ErrorResponse instance
    """
    if isinstance(error, CircuitBreakerOpenError):
        breaker = get_circuit_breaker()
        error_detail = create_circuit_breaker_open_error(
            remaining_timeout=breaker._get_remaining_timeout()
        )
    elif isinstance(error, OllamaUnavailableError):
        error_detail = create_service_unavailable_error(
            service="Ollama",
            cached_content_available=False,  # TODO: Check cache availability
        )
    elif isinstance(error, GenerationTimeoutError):
        error_detail = create_generation_timeout_error(
            timeout_seconds=60,
        )
    elif isinstance(error, MaxRetriesExceededError):
        error_detail = create_generation_failed_error(
            attempts=3,
            errors=[str(error)],
        )
    else:
        # Generic error
        error_detail = ErrorDetail(
            code="OLLAMA_ERROR",
            message="An error occurred while communicating with Ollama",
            details={"error": str(error)},
        )

    return ErrorResponse(
        error=error_detail,
        request_id=request_id,
    )


def check_ollama_health(base_url: str = "http://localhost:11434") -> bool:
    """Check if Ollama is running and accessible.

    Args:
        base_url: Ollama base URL

    Returns:
        True if Ollama is healthy, False otherwise
    """
    try:
        import requests

        response = requests.get(
            f"{base_url}/api/tags",
            timeout=2,
        )
        is_healthy = response.status_code == 200

        if not is_healthy:
            logger.warning(f"Ollama health check failed: status {response.status_code}")

        return is_healthy

    except Exception as e:
        logger.warning(f"Ollama health check exception: {e}")
        return False


def get_cached_result(cache_key: str) -> Optional[Dict[str, Any]]:
    """Get cached result if available.

    This is a placeholder for future caching implementation.
    Currently returns None to indicate no cache available.

    Args:
        cache_key: Cache key (e.g., topic hash)

    Returns:
        Cached result dict or None if not available
    """
    # TODO: Implement actual caching with SQLite
    # For now, return None to indicate no cache
    logger.debug(f"Cache check for key '{cache_key}': MISS (not implemented)")
    return None


def generate_with_fallback(
    generate_func: Callable[..., T],
    *args: Any,
    cache_key: Optional[str] = None,
    **kwargs: Any,
) -> T:
    """Generate with circuit breaker and fallback to cache.

    Attempts to generate content using circuit breaker protection.
    If Ollama is down, returns cached result if available.

    Args:
        generate_func: Function to call for generation
        *args: Positional arguments for generate_func
        cache_key: Optional cache key for fallback
        **kwargs: Keyword arguments for generate_func

    Returns:
        Generated content or cached result

    Raises:
        OllamaUnavailableError: If Ollama is down and no cache available
        CircuitBreakerOpenError: If circuit breaker is open
    """
    breaker = get_circuit_breaker()

    # Check Ollama health first
    if not check_ollama_health():
        logger.warning("Ollama health check failed, trying cache")

        # Try to return cached result
        if cache_key:
            cached = get_cached_result(cache_key)
            if cached:
                logger.info(f"Returning cached result for key '{cache_key}'")
                # Return cached data wrapped in expected format
                # Caller should handle this appropriately
                return cached  # type: ignore

        # No cache available
        raise OllamaUnavailableError(
            "Ollama service not running and no cached content available. "
            "Start Ollama with 'ollama serve' and try again."
        )

    # Use circuit breaker to call generate function
    return breaker.call(generate_func, *args, **kwargs)
