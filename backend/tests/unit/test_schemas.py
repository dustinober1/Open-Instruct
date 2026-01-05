"""
Unit tests for Pydantic schemas in api/schemas.py.

Tests cover:
- Valid inputs for all request/response schemas
- Invalid inputs and validation errors
- Field constraints and validators
- Edge cases
"""

import pytest
from datetime import datetime
from pydantic import ValidationError

from src.api.schemas import (
    DifficultyLevel,
    ErrorDetail,
    ErrorResponse,
    GenerateObjectivesRequest,
    GenerateObjectivesRequestOptions,
    GenerateQuizRequest,
    HealthResponse,
    LearningObjectiveResponse,
    MetaResponse,
    SuccessResponse,
)


# =============================================================================
# DifficultyLevel Enum Tests
# =============================================================================

class TestDifficultyLevel:
    """Test suite for DifficultyLevel enum."""

    def test_difficulty_level_values(self):
        """Test that all expected difficulty levels are present."""
        assert DifficultyLevel.EASY.value == "easy"
        assert DifficultyLevel.MEDIUM.value == "medium"
        assert DifficultyLevel.HARD.value == "hard"

    def test_difficulty_level_iteration(self):
        """Test iterating over all difficulty levels."""
        levels = list(DifficultyLevel)
        assert len(levels) == 3
        expected_levels = ["easy", "medium", "hard"]
        actual_levels = [level.value for level in levels]
        assert actual_levels == expected_levels


# =============================================================================
# GenerateObjectivesRequestOptions Tests
# =============================================================================

class TestGenerateObjectivesRequestOptions:
    """Test suite for GenerateObjectivesRequestOptions."""

    def test_default_values(self):
        """Test default field values."""
        options = GenerateObjectivesRequestOptions()
        assert options.force_cache_bypass is False
        assert options.include_explanations is False

    def test_with_custom_values(self):
        """Test with custom field values."""
        options = GenerateObjectivesRequestOptions(
            force_cache_bypass=True,
            include_explanations=True,
        )
        assert options.force_cache_bypass is True
        assert options.include_explanations is True


# =============================================================================
# GenerateObjectivesRequest Tests
# =============================================================================

class TestGenerateObjectivesRequest:
    """Test suite for GenerateObjectivesRequest."""

    def test_valid_request(self, valid_generate_objectives_request_data):
        """Test creating a valid request."""
        request = GenerateObjectivesRequest(**valid_generate_objectives_request_data)
        assert request.topic == "Introduction to Python Programming"
        assert request.target_audience == "Beginner developers"
        assert request.num_objectives == 6

    def test_default_num_objectives(self):
        """Test default num_objectives value."""
        request = GenerateObjectivesRequest(
            topic="Test Topic",
            target_audience="Test Audience",
        )
        assert request.num_objectives == 6

    def test_topic_min_length(self):
        """Test topic minimum length constraint."""
        with pytest.raises(ValidationError) as exc_info:
            GenerateObjectivesRequest(
                topic="",  # Empty topic
                target_audience="Test Audience",
            )
        errors = exc_info.value.errors()
        assert any(e["loc"] == ("topic",) for e in errors)

    def test_topic_max_length(self):
        """Test topic maximum length constraint."""
        long_topic = "a" * 201  # Exceeds 200 character limit
        with pytest.raises(ValidationError) as exc_info:
            GenerateObjectivesRequest(
                topic=long_topic,
                target_audience="Test Audience",
            )
        errors = exc_info.value.errors()
        assert any(e["loc"] == ("topic",) for e in errors)

    def test_target_audience_min_length(self):
        """Test target_audience minimum length constraint."""
        with pytest.raises(ValidationError) as exc_info:
            GenerateObjectivesRequest(
                topic="Test Topic",
                target_audience="",  # Empty audience
            )
        errors = exc_info.value.errors()
        assert any(e["loc"] == ("target_audience",) for e in errors)

    def test_target_audience_max_length(self):
        """Test target_audience maximum length constraint."""
        long_audience = "a" * 201  # Exceeds 200 character limit
        with pytest.raises(ValidationError) as exc_info:
            GenerateObjectivesRequest(
                topic="Test Topic",
                target_audience=long_audience,
            )
        errors = exc_info.value.errors()
        assert any(e["loc"] == ("target_audience",) for e in errors)

    @pytest.mark.parametrize("num_objectives", [0, 13, -1, 100])
    def test_num_objectives_out_of_range(self, num_objectives):
        """Test num_objectives outside valid range (1-12)."""
        with pytest.raises(ValidationError) as exc_info:
            GenerateObjectivesRequest(
                topic="Test Topic",
                target_audience="Test Audience",
                num_objectives=num_objectives,
            )
        errors = exc_info.value.errors()
        assert any(e["loc"] == ("num_objectives",) for e in errors)

    @pytest.mark.parametrize("num_objectives", [1, 6, 12])
    def test_num_objectives_valid_range(self, num_objectives):
        """Test num_objectives at valid range boundaries."""
        request = GenerateObjectivesRequest(
            topic="Test Topic",
            target_audience="Test Audience",
            num_objectives=num_objectives,
        )
        assert request.num_objectives == num_objectives

    def test_with_options(self):
        """Test request with options."""
        request = GenerateObjectivesRequest(
            topic="Test Topic",
            target_audience="Test Audience",
            num_objectives=5,
            options=GenerateObjectivesRequestOptions(
                force_cache_bypass=True,
                include_explanations=True,
            ),
        )
        assert request.options.force_cache_bypass is True
        assert request.options.include_explanations is True


# =============================================================================
# GenerateQuizRequest Tests
# =============================================================================

class TestGenerateQuizRequest:
    """Test suite for GenerateQuizRequest."""

    def test_valid_request(self, valid_generate_quiz_request_data):
        """Test creating a valid request."""
        request = GenerateQuizRequest(**valid_generate_quiz_request_data)
        assert request.objective_id == "LO-001"
        assert request.difficulty == DifficultyLevel.MEDIUM
        assert request.num_options == 4

    def test_default_difficulty(self):
        """Test default difficulty value."""
        request = GenerateQuizRequest(
            objective_id="LO-001",
        )
        assert request.difficulty == DifficultyLevel.MEDIUM

    def test_default_num_options(self):
        """Test default num_options value."""
        request = GenerateQuizRequest(
            objective_id="LO-001",
        )
        assert request.num_options == 4

    def test_objective_id_pattern_valid(self):
        """Test valid objective_id patterns."""
        valid_ids = ["LO-001", "LO-999", "LO-123"]
        for obj_id in valid_ids:
            request = GenerateQuizRequest(objective_id=obj_id)
            assert request.objective_id == obj_id

    def test_objective_id_pattern_invalid(self):
        """Test invalid objective_id patterns."""
        invalid_ids = [
            "LO-1",      # Too few digits
            "LO-1234",   # Too many digits
            "lo-001",    # Lowercase 'lo'
            "LO001",     # Missing hyphen
            "LO_001",    # Underscore instead of hyphen
            "L0-001",    # Zero instead of 'O'
            "L-001",     # Single letter
            "OBJECTIVE-001",  # Wrong prefix
        ]
        for obj_id in invalid_ids:
            with pytest.raises(ValidationError) as exc_info:
                GenerateQuizRequest(objective_id=obj_id)
            errors = exc_info.value.errors()
            assert any(e["loc"] == ("objective_id",) for e in errors)

    @pytest.mark.parametrize("difficulty", [DifficultyLevel.EASY, DifficultyLevel.MEDIUM, DifficultyLevel.HARD])
    def test_all_difficulty_levels(self, difficulty):
        """Test all difficulty level options."""
        request = GenerateQuizRequest(
            objective_id="LO-001",
            difficulty=difficulty,
        )
        assert request.difficulty == difficulty

    @pytest.mark.parametrize("num_options", [3, 5, 2, 10])
    def test_num_options_not_four(self, num_options):
        """Test num_options that are not 4 (should fail)."""
        with pytest.raises(ValidationError) as exc_info:
            GenerateQuizRequest(
                objective_id="LO-001",
                num_options=num_options,
            )
        errors = exc_info.value.errors()
        assert any(e["loc"] == ("num_options",) for e in errors)


# =============================================================================
# LearningObjectiveResponse Tests
# =============================================================================

class TestLearningObjectiveResponse:
    """Test suite for LearningObjectiveResponse."""

    def test_valid_response(self):
        """Test creating a valid response."""
        response = LearningObjectiveResponse(
            id="LO-001",
            verb="explain",
            content="test content",
            level="Understand",
            explanation="Test explanation",
        )
        assert response.id == "LO-001"
        assert response.verb == "explain"
        assert response.explanation == "Test explanation"

    def test_without_explanation(self):
        """Test response without explanation (optional field)."""
        response = LearningObjectiveResponse(
            id="LO-001",
            verb="explain",
            content="test content",
            level="Understand",
            explanation=None,
        )
        assert response.explanation is None


# =============================================================================
# MetaResponse Tests
# =============================================================================

class TestMetaResponse:
    """Test suite for MetaResponse."""

    def test_valid_meta_response(self):
        """Test creating a valid meta response."""
        meta = MetaResponse(
            request_id="req_abc123",
            timestamp=datetime.utcnow(),
            processing_time_ms=150,
        )
        assert meta.request_id == "req_abc123"
        assert meta.processing_time_ms == 150
        assert isinstance(meta.timestamp, datetime)

    def test_processing_time_boundary_values(self):
        """Test processing time at boundaries."""
        # Very small processing time
        meta = MetaResponse(
            request_id="req_001",
            timestamp=datetime.utcnow(),
            processing_time_ms=1,
        )
        assert meta.processing_time_ms == 1

        # Large processing time
        meta = MetaResponse(
            request_id="req_002",
            timestamp=datetime.utcnow(),
            processing_time_ms=60000,  # 1 minute
        )
        assert meta.processing_time_ms == 60000


# =============================================================================
# SuccessResponse Tests
# =============================================================================

class TestSuccessResponse:
    """Test suite for SuccessResponse."""

    def test_valid_success_response(self):
        """Test creating a valid success response."""
        meta = MetaResponse(
            request_id="req_001",
            timestamp=datetime.utcnow(),
            processing_time_ms=100,
        )
        response = SuccessResponse(
            success=True,
            data={"test": "data"},
            meta=meta,
        )
        assert response.success is True
        assert response.data == {"test": "data"}
        assert response.meta.request_id == "req_001"

    def test_default_success_value(self):
        """Test default success value."""
        meta = MetaResponse(
            request_id="req_001",
            timestamp=datetime.utcnow(),
            processing_time_ms=100,
        )
        response = SuccessResponse(
            data={"test": "data"},
            meta=meta,
        )
        assert response.success is True  # Should default to True


# =============================================================================
# ErrorDetail Tests
# =============================================================================

class TestErrorDetail:
    """Test suite for ErrorDetail."""

    def test_valid_error_detail(self):
        """Test creating a valid error detail."""
        error = ErrorDetail(
            code="TEST_ERROR",
            message="Test error message",
            details={"key": "value"},
        )
        assert error.code == "TEST_ERROR"
        assert error.message == "Test error message"
        assert error.details == {"key": "value"}

    def test_without_details(self):
        """Test error detail without details (optional field)."""
        error = ErrorDetail(
            code="TEST_ERROR",
            message="Test error message",
        )
        assert error.details is None


# =============================================================================
# ErrorResponse Tests
# =============================================================================

class TestErrorResponse:
    """Test suite for ErrorResponse."""

    def test_valid_error_response(self):
        """Test creating a valid error response."""
        meta = MetaResponse(
            request_id="req_001",
            timestamp=datetime.utcnow(),
            processing_time_ms=50,
        )
        error = ErrorDetail(
            code="TEST_ERROR",
            message="Test error",
        )
        response = ErrorResponse(
            success=False,
            error=error,
            meta=meta,
        )
        assert response.success is False
        assert response.error.code == "TEST_ERROR"
        assert response.meta.request_id == "req_001"

    def test_default_success_value(self):
        """Test default success value is False."""
        meta = MetaResponse(
            request_id="req_001",
            timestamp=datetime.utcnow(),
            processing_time_ms=50,
        )
        error = ErrorDetail(
            code="TEST_ERROR",
            message="Test error",
        )
        response = ErrorResponse(
            error=error,
            meta=meta,
        )
        assert response.success is False  # Should default to False


# =============================================================================
# HealthResponse Tests
# =============================================================================

class TestHealthResponse:
    """Test suite for HealthResponse."""

    def test_valid_health_response(self):
        """Test creating a valid health response."""
        response = HealthResponse(
            status="healthy",
            ollama_connected=True,
            model_version="llama3.1",
            version="1.0.0",
            uptime_seconds=123.45,
        )
        assert response.status == "healthy"
        assert response.ollama_connected is True
        assert response.model_version == "llama3.1"

    def test_without_model_version(self):
        """Test health response without model version (optional)."""
        response = HealthResponse(
            status="degraded",
            ollama_connected=False,
            model_version=None,
            version="1.0.0",
            uptime_seconds=100.0,
        )
        assert response.model_version is None

    @pytest.mark.parametrize("status", ["healthy", "degraded", "error"])
    def test_different_status_values(self, status):
        """Test different status values."""
        response = HealthResponse(
            status=status,
            ollama_connected=True,
            model_version="llama3.1",
            version="1.0.0",
            uptime_seconds=100.0,
        )
        assert response.status == status

    def test_uptime_boundary_values(self):
        """Test uptime at boundary values."""
        # Just started
        response = HealthResponse(
            status="healthy",
            ollama_connected=True,
            model_version="llama3.1",
            version="1.0.0",
            uptime_seconds=0.1,
        )
        assert response.uptime_seconds == 0.1

        # Long uptime
        response = HealthResponse(
            status="healthy",
            ollama_connected=True,
            model_version="llama3.1",
            version="1.0.0",
            uptime_seconds=86400.0,  # 1 day
        )
        assert response.uptime_seconds == 86400.0


# =============================================================================
# Edge Cases and Boundary Conditions
# =============================================================================

class TestSchemaEdgeCases:
    """Test edge cases for API schemas."""

    def test_topic_with_special_characters(self):
        """Test topic with special characters."""
        request = GenerateObjectivesRequest(
            topic="Python & Django: Web Development! (2024 Edition)",
            target_audience="Test Audience",
        )
        assert "&" in request.topic
        assert "!" in request.topic

    def test_topic_with_unicode(self):
        """Test topic with unicode characters."""
        request = GenerateObjectivesRequest(
            topic="机器学习基础",
            target_audience="Test Audience",
        )
        assert request.topic == "机器学习基础"

    def test_request_id_formats(self):
        """Test different request ID formats."""
        valid_ids = [
            "req_abc123def456",
            "req_1",
            "req_A1B2C3",
        ]
        for req_id in valid_ids:
            meta = MetaResponse(
                request_id=req_id,
                timestamp=datetime.utcnow(),
                processing_time_ms=100,
            )
            assert meta.request_id == req_id

    def test_whitespace_handling(self):
        """Test handling of whitespace in fields."""
        request = GenerateObjectivesRequest(
            topic="  Test Topic  ",  # Leading/trailing spaces preserved
            target_audience="Test Audience",
        )
        assert request.topic == "  Test Topic  "

    def test_newlines_in_audience(self):
        """Test handling newlines in target audience."""
        audience = "Beginner developers\nWith some experience"
        request = GenerateObjectivesRequest(
            topic="Test Topic",
            target_audience=audience,
        )
        assert "\n" in request.target_audience
