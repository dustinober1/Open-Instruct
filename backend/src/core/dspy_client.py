"""
DSPy client configuration for Ollama integration.

This module configures DSPy to use Ollama as the LLM provider for local inference,
specifically targeting the DeepSeek-R1 1.5B model. It provides connection testing,
configuration management, and graceful error handling for Ollama connectivity issues.

DSPy 2.x uses LiteLLM under the hood, which supports Ollama via the 'ollama/' prefix.
"""

import os
from typing import Optional

import dspy
from dspy.clients.lm import LM
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class DSPyClientError(Exception):
    """Base exception for DSPy client errors."""

    pass


class OllamaConnectionError(DSPyClientError):
    """Exception raised when Ollama connection fails."""

    pass


class OllamaConfigError(DSPyClientError):
    """Exception raised when Ollama configuration is invalid."""

    pass


def configure_dspy(
    base_url: Optional[str] = None,
    model: Optional[str] = None,
    timeout: int = 30,
) -> LM:
    """
    Configure DSPy to use Ollama as the language model provider.

    This function sets up the DSPy environment with Ollama, using environment
    variables as defaults for the base URL and model name. It validates the
    configuration before returning the configured LM instance.

    Note: DSPy 2.x uses LiteLLM, which accesses Ollama via the 'ollama/' prefix.
    For example, to use deepseek-r1:1.5b, the model string should be 'ollama/deepseek-r1:1.5b'.

    Args:
        base_url: Ollama server URL (defaults to OLLAMA_BASE_URL env var or http://localhost:11434)
        model: Model name to use (defaults to OLLAMA_MODEL env var or deepseek-r1:1.5b).
               The 'ollama/' prefix will be added automatically if not present.
        timeout: Request timeout in seconds (default: 30)

    Returns:
        Configured dspy.clients.lm.LM instance

    Raises:
        OllamaConfigError: If configuration is invalid
        OllamaConnectionError: If Ollama server is not accessible

    Example:
        >>> lm = configure_dspy()
        >>> dspy.configure(lm=lm)
        >>> # Use DSPy modules...
    """
    # Get configuration from environment or use defaults
    base_url = base_url or os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    model = model or os.getenv("OLLAMA_MODEL", "deepseek-r1:1.5b")

    # Validate configuration
    if not base_url:
        raise OllamaConfigError("Ollama base URL is not configured")

    if not model:
        raise OllamaConfigError("Ollama model is not configured")

    # Add 'ollama/' prefix if not present (required by LiteLLM)
    if not model.startswith("ollama/"):
        model = f"ollama/{model}"

    # Configure DSPy with Ollama
    try:
        lm = LM(
            model=model,
            base_url=base_url,
            timeout=timeout,
        )

        # Set as default DSPy LM
        dspy.configure(lm=lm)

        return lm

    except Exception as e:
        raise OllamaConfigError(f"Failed to configure DSPy with Ollama: {e}")


def test_ollama_connection(base_url: Optional[str] = None) -> dict:
    """
    Test if Ollama server is running and accessible.

    This function attempts to connect to the Ollama server and verify it's
    responding to requests. It provides detailed diagnostics for troubleshooting.

    Args:
        base_url: Ollama server URL (defaults to OLLAMA_BASE_URL env var or http://localhost:11434)

    Returns:
        Dictionary with connection status and diagnostics:
        {
            "status": "ok" | "error",
            "message": str,
            "base_url": str,
            "error": Optional[str]
        }

    Example:
        >>> result = test_ollama_connection()
        >>> if result["status"] == "ok":
        ...     print("Ollama is ready!")
        ... else:
        ...     print(f"Connection failed: {result['error']}")
    """
    import requests

    base_url = base_url or os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")

    result = {
        "status": "error",
        "message": "",
        "base_url": base_url,
        "error": None,
    }

    try:
        # Try to reach Ollama's /api/tags endpoint (lists available models)
        response = requests.get(f"{base_url}/api/tags", timeout=5)

        if response.status_code == 200:
            result["status"] = "ok"
            result["message"] = "Ollama is running and accessible"
            return result
        else:
            result["error"] = f"Ollama returned status {response.status_code}"
            result["message"] = "Ollama server responded but with unexpected status"
            return result

    except requests.exceptions.ConnectionError:
        result["error"] = (
            f"Cannot connect to Ollama at {base_url}. "
            f"Ensure Ollama is running with 'ollama serve'"
        )
        result["message"] = "Connection refused - Ollama not running?"
        return result

    except requests.exceptions.Timeout:
        result["error"] = f"Connection to Ollama at {base_url} timed out"
        result["message"] = "Connection timed out"
        return result

    except Exception as e:
        result["error"] = f"Unexpected error: {str(e)}"
        result["message"] = "Unexpected error during connection test"
        return result


def verify_model_availability(model: Optional[str] = None, base_url: Optional[str] = None) -> dict:
    """
    Check if a specific model is available in Ollama.

    Args:
        model: Model name to check (defaults to OLLAMA_MODEL env var or deepseek-r1:1.5b)
        base_url: Ollama server URL (defaults to OLLAMA_BASE_URL env var or http://localhost:11434)

    Returns:
        Dictionary with model availability status:
        {
            "status": "available" | "unavailable" | "error",
            "message": str,
            "model": str,
            "installed_models": List[str]
        }

    Example:
        >>> result = verify_model_availability("deepseek-r1:1.5b")
        >>> if result["status"] == "available":
        ...     print("Model is ready!")
        ... else:
        ...     print(f"Model not found. Available: {result['installed_models']}")
    """
    import requests

    base_url = base_url or os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    model = model or os.getenv("OLLAMA_MODEL", "deepseek-r1:1.5b")

    result = {
        "status": "error",
        "message": "",
        "model": model,
        "installed_models": [],
    }

    try:
        # Get list of installed models
        response = requests.get(f"{base_url}/api/tags", timeout=5)

        if response.status_code != 200:
            result["status"] = "error"
            result["message"] = f"Failed to get model list: HTTP {response.status_code}"
            return result

        data = response.json()
        installed_models = [m["name"] for m in data.get("models", [])]
        result["installed_models"] = installed_models

        # Check if requested model is available
        if model in installed_models:
            result["status"] = "available"
            result["message"] = f"Model '{model}' is available"
            return result
        else:
            result["status"] = "unavailable"
            result["message"] = (
                f"Model '{model}' not found in Ollama. "
                f"Install it with: ollama pull {model}"
            )
            return result

    except requests.exceptions.ConnectionError:
        result["message"] = "Cannot connect to Ollama server"
        return result
    except Exception as e:
        result["message"] = f"Error checking model availability: {str(e)}"
        return result


def get_configured_lm() -> LM:
    """
    Get the currently configured DSPy language model.

    Returns:
        The currently configured dspy.clients.lm.LM instance

    Raises:
        DSPyClientError: If no LM has been configured
    """
    try:
        # DSPy stores the configured LM in settings.config
        if dspy.settings.config.get("lm") is None:
            raise DSPyClientError("No DSPy LM has been configured. Call configure_dspy() first.")
        return dspy.settings.config["lm"]

    except DSPyClientError:
        raise
    except Exception as e:
        raise DSPyClientError(f"Failed to get configured LM: {e}")


def get_model_info() -> dict:
    """
    Get information about the currently configured model.

    Returns:
        Dictionary with model configuration details:
        {
            "model": str,
            "base_url": str,
            "provider": "ollama",
            "configured": bool
        }

    Example:
        >>> info = get_model_info()
        >>> print(f"Using {info['model']} at {info['base_url']}")
    """
    info = {
        "model": os.getenv("OLLAMA_MODEL", "deepseek-r1:1.5b"),
        "base_url": os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
        "provider": "ollama",
        "configured": False,
    }

    try:
        lm = get_configured_lm()
        # Check if it's configured for Ollama
        if hasattr(lm, "model") and lm.model.startswith("ollama/"):
            info["configured"] = True
            info["model"] = lm.model
            # LM doesn't store base_url directly, it's passed to the provider
            info["base_url"] = getattr(lm, "base_url", os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"))
    except DSPyClientError:
        pass

    return info


# Convenience function for quick setup
def setup_dspy_with_ollama(
    auto_test: bool = True,
    raise_on_error: bool = False,
) -> LM:
    """
    Quick setup function that configures DSPy and optionally tests the connection.

    This is a convenience function that combines configure_dspy() and
    test_ollama_connection() for easy initialization.

    Args:
        auto_test: Whether to automatically test the connection (default: True)
        raise_on_error: Whether to raise exception on connection failure (default: False)

    Returns:
        Configured dspy.lm.Ollama instance

    Raises:
        OllamaConnectionError: If raise_on_error=True and connection fails

    Example:
        >>> # Quick setup with automatic testing
        >>> lm = setup_dspy_with_ollama()
        >>>
        >>> # Setup without testing
        >>> lm = setup_dspy_with_ollama(auto_test=False)
        >>>
        >>> # Setup with error handling
        >>> try:
        ...     lm = setup_dspy_with_ollama(raise_on_error=True)
        ... except OllamaConnectionError as e:
        ...     print(f"Setup failed: {e}")
    """
    # Test connection if requested
    if auto_test:
        result = test_ollama_connection()
        if result["status"] != "ok":
            error_msg = f"Ollama connection test failed: {result['error']}"
            if raise_on_error:
                raise OllamaConnectionError(error_msg)
            else:
                print(f"Warning: {error_msg}")

    # Configure DSPy
    lm = configure_dspy()

    return lm
