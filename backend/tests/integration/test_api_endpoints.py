"""
Integration tests for FastAPI endpoints with mock Ollama responses.

Tests cover:
- Health endpoint
- Objectives generation endpoint
- Quiz generation endpoint
- Error scenarios
- Request validation
"""

import json
from unittest.mock import patch, Mock
from datetime import datetime

import pytest
from fastapi.testclient import TestClient

from src.api.main import app


# =============================================================================
# Test Client Fixture
# =============================================================================

@pytest.fixture
def client():
    """Create a test client for the FastAPI app."""
    return TestClient(app)


# =============================================================================
# Health Endpoint Tests
# =============================================================================

class TestHealthEndpoint:
    """Test suite for /health endpoint."""

    @patch('src.api.main.test_ollama_connection')
    @patch('src.api.main.check_ollama_health')
    @patch('src.api.main.get_model_info')
    @patch('src.api.main.get_circuit_breaker')
    def test_health_check_healthy(
        self,
        mock_get_circuit_breaker,
        mock_get_model_info,
        mock_check_ollama_health,
        mock_test_ollama_connection,
        client,
    ):
        """Test health check returns healthy status."""
        # Setup mocks
        mock_test_ollama_connection.return_value = {"status": "ok"}
        mock_check_ollama_health.return_value = True
        mock_get_model_info.return_value = {"model": "llama3.1"}

        from src.core.error_handlers import CircuitState, CircuitBreaker
        mock_cb = Mock(spec=CircuitBreaker)
        mock_cb.state = CircuitState.CLOSED
        mock_get_circuit_breaker.return_value = mock_cb

        response = client.get("/health")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["ollama_connected"] is True
        assert data["model_version"] == "llama3.1"
        assert "uptime_seconds" in data

    @patch('src.api.main.test_ollama_connection')
    @patch('src.api.main.check_ollama_health')
    @patch('src.api.main.get_model_info')
    @patch('src.api.main.get_circuit_breaker')
    def test_health_check_degraded(
        self,
        mock_get_circuit_breaker,
        mock_get_model_info,
        mock_check_ollama_health,
        mock_test_ollama_connection,
        client,
    ):
        """Test health check returns degraded status when Ollama is down."""
        # Setup mocks
        mock_test_ollama_connection.return_value = {"status": "error"}
        mock_check_ollama_health.return_value = False
        mock_get_model_info.return_value = {}

        from src.core.error_handlers import CircuitState, CircuitBreaker
        mock_cb = Mock(spec=CircuitBreaker)
        mock_cb.state = CircuitState.CLOSED
        mock_get_circuit_breaker.return_value = mock_cb

        response = client.get("/health")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "degraded"
        assert data["ollama_connected"] is False

    @patch('src.api.main.test_ollama_connection')
    @patch('src.api.main.check_ollama_health')
    @patch('src.api.main.get_model_info')
    @patch('src.api.main.get_circuit_breaker')
    def test_health_check_circuit_breaker_open(
        self,
        mock_get_circuit_breaker,
        mock_get_model_info,
        mock_check_ollama_health,
        mock_test_ollama_connection,
        client,
    ):
        """Test health check returns degraded status when circuit breaker is open."""
        # Setup mocks
        mock_test_ollama_connection.return_value = {"status": "ok"}
        mock_check_ollama_health.return_value = True
        mock_get_model_info.return_value = {"model": "llama3.1"}

        from src.core.error_handlers import CircuitState, CircuitBreaker
        mock_cb = Mock(spec=CircuitBreaker)
        mock_cb.state = CircuitState.OPEN
        mock_get_circuit_breaker.return_value = mock_cb

        response = client.get("/health")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "degraded"

    def test_health_check_error_handling(self, client):
        """Test health check handles exceptions gracefully."""
        response = client.get("/health")

        # Should always return 200, even with errors
        assert response.status_code == 200
        data = response.json()
        assert "status" in data


# =============================================================================
# Root Endpoint Tests
# =============================================================================

class TestRootEndpoint:
    """Test suite for root endpoint."""

    def test_root_endpoint(self, client):
        """Test root endpoint returns API information."""
        response = client.get("/")

        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Open-Instruct API"
        assert data["version"] == "1.0.0"
        assert "docs" in data
        assert "health" in data


# =============================================================================
# Objectives Generation Endpoint Tests
# =============================================================================

class TestObjectivesGenerationEndpoint:
    """Test suite for /api/v1/generate/objectives endpoint."""

    @patch('src.api.main.configure_dspy')
    @patch('src.api.main.Architect')
    @patch('src.api.main.generate_with_fallback')
    @patch('src.api.main.get_objective_store')
    def test_generate_objectives_success(
        self,
        mock_get_objective_store,
        mock_generate_with_fallback,
        mock_architect_class,
        mock_configure_dspy,
        client,
        sample_learning_objectives,
    ):
        """Test successful objectives generation."""
        # Setup mocks
        mock_configure_dspy.return_value = None

        from src.core.models import CourseStructure
        mock_course_structure = CourseStructure(
            topic="Introduction to Python",
            objectives=sample_learning_objectives[:3],
        )
        mock_generate_with_fallback.return_value = mock_course_structure

        mock_store = Mock()
        mock_store.add_objectives.return_value = None
        mock_get_objective_store.return_value = mock_store

        # Make request
        request_data = {
            "topic": "Introduction to Python",
            "target_audience": "Beginner developers",
            "num_objectives": 3,
        }
        response = client.post("/api/v1/generate/objectives", json=request_data)

        # Verify response
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "data" in data
        assert "meta" in data
        assert data["data"]["topic"] == "Introduction to Python"
        assert len(data["data"]["objectives"]) == 3

    @patch('src.api.main.configure_dspy')
    @patch('src.api.main.Architect')
    @patch('src.api.main.generate_with_fallback')
    @patch('src.api.main.get_objective_store')
    def test_generate_objectives_with_options(
        self,
        mock_get_objective_store,
        mock_generate_with_fallback,
        mock_architect_class,
        mock_configure_dspy,
        client,
        sample_learning_objectives,
    ):
        """Test objectives generation with options."""
        # Setup mocks
        mock_configure_dspy.return_value = None

        from src.core.models import CourseStructure
        mock_course_structure = CourseStructure(
            topic="Test Topic",
            objectives=sample_learning_objectives[:3],
        )
        mock_generate_with_fallback.return_value = mock_course_structure

        mock_store = Mock()
        mock_store.add_objectives.return_value = None
        mock_get_objective_store.return_value = mock_store

        # Make request with options
        request_data = {
            "topic": "Test Topic",
            "target_audience": "Test Audience",
            "num_objectives": 3,
            "options": {
                "force_cache_bypass": True,
                "include_explanations": True,
            },
        }
        response = client.post("/api/v1/generate/objectives", json=request_data)

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True

    def test_generate_objectives_validation_error(self, client):
        """Test validation error for invalid request."""
        request_data = {
            "topic": "",  # Empty topic (invalid)
            "target_audience": "Test Audience",
            "num_objectives": 3,
        }
        response = client.post("/api/v1/generate/objectives", json=request_data)

        assert response.status_code in [400, 422]  # 422 for Pydantic validation
        data = response.json()
        assert "error" in data or "detail" in data

    def test_generate_objectives_missing_field(self, client):
        """Test validation error for missing required field."""
        request_data = {
            "topic": "Test Topic",
            # Missing target_audience
            "num_objectives": 3,
        }
        response = client.post("/api/v1/generate/objectives", json=request_data)

        assert response.status_code in [400, 422]  # 422 for Pydantic validation
        data = response.json()
        assert "error" in data or "detail" in data

    @patch('src.api.main.configure_dspy')
    def test_generate_objectives_ollama_unavailable(self, mock_configure_dspy, client):
        """Test handling when Ollama is unavailable."""
        mock_configure_dspy.side_effect = Exception("Ollama not available")

        request_data = {
            "topic": "Test Topic",
            "target_audience": "Test Audience",
            "num_objectives": 3,
        }
        response = client.post("/api/v1/generate/objectives", json=request_data)

        assert response.status_code == 503
        data = response.json()
        assert "error" in data or "detail" in data


# =============================================================================
# Quiz Generation Endpoint Tests
# =============================================================================

class TestQuizGenerationEndpoint:
    """Test suite for /api/v1/generate/quiz endpoint."""

    @patch('src.api.main.configure_dspy')
    @patch('src.api.main.Assessor')
    @patch('src.api.main.generate_with_fallback')
    @patch('src.api.main.get_objective_store')
    def test_generate_quiz_success(
        self,
        mock_get_objective_store,
        mock_generate_with_fallback,
        mock_assessor_class,
        mock_configure_dspy,
        client,
        valid_quiz_question,
    ):
        """Test successful quiz generation."""
        # Setup mocks
        mock_configure_dspy.return_value = None
        mock_generate_with_fallback.return_value = valid_quiz_question

        from src.core.models import LearningObjective, BloomLevel
        mock_objective = LearningObjective(
            id="LO-001",
            verb="explain",
            content="test content",
            level=BloomLevel.UNDERSTAND,
        )

        mock_store = Mock()
        mock_store.get_objective.return_value = mock_objective
        mock_get_objective_store.return_value = mock_store

        # Make request
        request_data = {
            "objective_id": "LO-001",
            "difficulty": "medium",
        }
        response = client.post("/api/v1/generate/quiz", json=request_data)

        # Verify response
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "data" in data
        assert "meta" in data
        assert data["data"]["stem"] == valid_quiz_question.stem
        assert data["data"]["correct_answer"] == valid_quiz_question.correct_answer
        assert len(data["data"]["distractors"]) == 3

    @patch('src.api.main.get_objective_store')
    def test_generate_quiz_objective_not_found(self, mock_get_objective_store, client):
        """Test quiz generation when objective not found."""
        # Setup mock
        mock_store = Mock()
        mock_store.get_objective.return_value = None
        mock_get_objective_store.return_value = mock_store

        request_data = {
            "objective_id": "LO-999",
            "difficulty": "medium",
        }
        response = client.post("/api/v1/generate/quiz", json=request_data)

        assert response.status_code == 404
        data = response.json()
        assert "OBJECTIVE_NOT_FOUND" in str(data)

    def test_generate_quiz_invalid_objective_id(self, client):
        """Test validation error for invalid objective ID format."""
        request_data = {
            "objective_id": "invalid-id",  # Doesn't match LO-XXX pattern
            "difficulty": "medium",
        }
        response = client.post("/api/v1/generate/quiz", json=request_data)

        assert response.status_code in [400, 422]  # 422 for Pydantic validation
        data = response.json()
        assert "error" in data or "detail" in data

    def test_generate_quiz_missing_objective_id(self, client):
        """Test validation error for missing objective_id."""
        request_data = {
            # Missing objective_id
            "difficulty": "medium",
        }
        response = client.post("/api/v1/generate/quiz", json=request_data)

        assert response.status_code in [400, 422]  # 422 for Pydantic validation

    @patch('src.api.main.configure_dspy')
    @patch('src.api.main.get_objective_store')
    def test_generate_quiz_ollama_unavailable(
        self,
        mock_get_objective_store,
        mock_configure_dspy,
        client,
    ):
        """Test quiz generation when Ollama is unavailable."""
        # Setup mocks
        mock_configure_dspy.side_effect = Exception("Ollama not available")

        from src.core.models import LearningObjective, BloomLevel
        mock_objective = LearningObjective(
            id="LO-001",
            verb="explain",
            content="test content",
            level=BloomLevel.UNDERSTAND,
        )
        mock_store = Mock()
        mock_store.get_objective.return_value = mock_objective
        mock_get_objective_store.return_value = mock_store

        request_data = {
            "objective_id": "LO-001",
            "difficulty": "medium",
        }
        response = client.post("/api/v1/generate/quiz", json=request_data)

        assert response.status_code == 503
        data = response.json()
        assert "error" in data or "detail" in data


# =============================================================================
# Error Response Tests
# =============================================================================

class TestErrorResponses:
    """Test suite for error response format."""

    def test_404_response(self, client):
        """Test 404 error response format."""
        response = client.get("/nonexistent-endpoint")

        assert response.status_code == 404

    def test_405_response(self, client):
        """Test 405 method not allowed."""
        response = client.post("/health")

        assert response.status_code == 405

    def test_error_response_has_required_fields(self, client):
        """Test that error responses have required fields."""
        response = client.post("/api/v1/generate/objectives", json={})

        assert response.status_code in [400, 422]  # 422 for Pydantic validation
        data = response.json()
        # Should have error information
        assert "detail" in data or "error" in data


# =============================================================================
# CORS Tests
# =============================================================================

class TestCORS:
    """Test suite for CORS middleware."""

    def test_cors_headers_present(self, client):
        """Test that CORS headers are present in response."""
        response = client.get("/health", headers={"Origin": "http://localhost:3000"})

        # Check for CORS headers
        assert "access-control-allow-origin" in response.headers


# =============================================================================
# Request ID Tests
# =============================================================================

class TestRequestID:
    """Test suite for request ID handling."""

    @patch('src.api.main.configure_dspy')
    @patch('src.api.main.Architect')
    @patch('src.api.main.generate_with_fallback')
    @patch('src.api.main.get_objective_store')
    def test_response_has_request_id(
        self,
        mock_get_objective_store,
        mock_generate_with_fallback,
        mock_architect_class,
        mock_configure_dspy,
        client,
        sample_learning_objectives,
    ):
        """Test that response includes request ID."""
        # Setup mocks
        mock_configure_dspy.return_value = None

        from src.core.models import CourseStructure
        mock_course_structure = CourseStructure(
            topic="Test Topic",
            objectives=sample_learning_objectives[:3],
        )
        mock_generate_with_fallback.return_value = mock_course_structure

        mock_store = Mock()
        mock_store.add_objectives.return_value = None
        mock_get_objective_store.return_value = mock_store

        request_data = {
            "topic": "Test Topic",
            "target_audience": "Test Audience",
            "num_objectives": 3,
        }
        response = client.post("/api/v1/generate/objectives", json=request_data)

        assert response.status_code == 200
        data = response.json()
        assert "meta" in data
        assert "request_id" in data["meta"]
        assert data["meta"]["request_id"].startswith("req_")

    @patch('src.api.main.configure_dspy')
    @patch('src.api.main.Architect')
    @patch('src.api.main.generate_with_fallback')
    @patch('src.api.main.get_objective_store')
    def test_response_has_processing_time(
        self,
        mock_get_objective_store,
        mock_generate_with_fallback,
        mock_architect_class,
        mock_configure_dspy,
        client,
        sample_learning_objectives,
    ):
        """Test that response includes processing time."""
        # Setup mocks
        mock_configure_dspy.return_value = None

        from src.core.models import CourseStructure
        mock_course_structure = CourseStructure(
            topic="Test Topic",
            objectives=sample_learning_objectives[:3],
        )
        mock_generate_with_fallback.return_value = mock_course_structure

        mock_store = Mock()
        mock_store.add_objectives.return_value = None
        mock_get_objective_store.return_value = mock_store

        request_data = {
            "topic": "Test Topic",
            "target_audience": "Test Audience",
            "num_objectives": 3,
        }
        response = client.post("/api/v1/generate/objectives", json=request_data)

        assert response.status_code == 200
        data = response.json()
        assert "meta" in data
        assert "processing_time_ms" in data["meta"]
        assert isinstance(data["meta"]["processing_time_ms"], int)
