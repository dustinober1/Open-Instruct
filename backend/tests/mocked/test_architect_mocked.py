"""
Mocked tests for Architect DSPy module.

Tests cover:
- Mocked LLM responses (no actual Ollama calls)
- Prompt logic verification
- Bloom's verb validation with mocked data
- Error handling with mock failures
- Edge cases with various mocked scenarios
"""

import json
from unittest.mock import Mock, patch, MagicMock

import pytest
import dspy

from src.core.models import BloomLevel, CourseStructure, LearningObjective
from src.modules.architect import Architect, GenerateObjectives


# =============================================================================
# Mock Response Fixtures
# =============================================================================

@pytest.fixture
def mock_architect_response():
    """Mock successful Architect LLM response."""
    return {
        "topic": "Introduction to Machine Learning",
        "objectives": [
            {
                "id": "LO-001",
                "verb": "define",
                "content": "machine learning and its core components",
                "level": "Remember"
            },
            {
                "id": "LO-002",
                "verb": "explain",
                "content": "the differences between supervised and unsupervised learning",
                "level": "Understand"
            },
            {
                "id": "LO-003",
                "verb": "apply",
                "content": "scikit-learn to train a basic classification model",
                "level": "Apply"
            }
        ]
    }


@pytest.fixture
def mock_invalid_verb_response():
    """Mock response with invalid Bloom's verb (for validation testing)."""
    return {
        "topic": "Test Topic",
        "objectives": [
            {
                "id": "LO-001",
                "verb": "code",  # Invalid verb for "Remember" level
                "content": "test content",
                "level": "Remember"
            }
        ]
    }


@pytest.fixture
def mock_wrong_count_response():
    """Mock response with wrong objective count."""
    return {
        "topic": "Test Topic",
        "objectives": [
            {
                "id": "LO-001",
                "verb": "explain",
                "content": "test content",
                "level": "Understand"
            }
            # Requested 3, but only got 1
        ]
    }


# =============================================================================
# Architect Initialization Tests
# =============================================================================

class TestArchitectInit:
    """Test suite for Architect initialization."""

    @patch('src.modules.architect.dspy.Predict.__init__')
    def test_architect_initialization(self, mock_predict_init):
        """Test Architect module initialization."""
        mock_predict_init.return_value = None
        architect = Architect()
        assert architect is not None

    @patch('src.modules.architect.dspy.Predict.__init__')
    def test_architect_with_custom_kwargs(self, mock_predict_init):
        """Test Architect initialization with custom kwargs."""
        mock_predict_init.return_value = None
        architect = Architect(temperature=0.7, max_tokens=1000)
        assert architect is not None


# =============================================================================
# Mocked Generation Tests
# =============================================================================

class TestArchitectMockedGeneration:
    """Test suite for mocked Architect generation."""

    @patch('src.modules.architect.dspy.Predict.forward')
    def test_generate_objectives_with_mock(self, mock_forward, mock_architect_response):
        """Test generating objectives with mocked LLM response."""
        # Setup mock prediction
        mock_prediction = Mock()
        mock_prediction.course_structure = mock_architect_response
        mock_forward.return_value = mock_prediction

        # Create architect and generate
        architect = Architect()
        result = architect.generate_objectives(
            topic="Introduction to Machine Learning",
            target_audience="Junior developers",
            num_objectives=3,
        )

        # Verify result
        assert isinstance(result, CourseStructure)
        assert result.topic == "Introduction to Machine Learning"
        assert len(result.objectives) == 3
        assert result.objectives[0].verb == "define"

        # Verify LLM was called
        mock_forward.assert_called_once()

    @patch('src.modules.architect.dspy.Predict.forward')
    def test_forward_returns_prediction(self, mock_forward, mock_architect_response):
        """Test that forward method returns object with course_structure."""
        mock_prediction = Mock()
        mock_prediction.course_structure = mock_architect_response
        mock_forward.return_value = mock_prediction

        architect = Architect()
        prediction = architect.forward(
            topic="Test Topic",
            target_audience="Test Audience",
            num_objectives=3,
        )

        # With mocking, we get a Mock back - just verify it has the right structure
        assert hasattr(prediction, 'course_structure')

    @patch('src.modules.architect.dspy.Predict.forward')
    def test_generate_with_dict_response(self, mock_forward, mock_architect_response):
        """Test generating when LLM returns dict (not CourseStructure)."""
        mock_prediction = Mock()
        mock_prediction.course_structure = mock_architect_response  # Dict, not CourseStructure
        mock_forward.return_value = mock_prediction

        architect = Architect()
        result = architect.generate_objectives(
            topic="Test Topic",
            target_audience="Test Audience",
            num_objectives=3,
        )

        # Should convert dict to CourseStructure
        assert isinstance(result, CourseStructure)
        assert len(result.objectives) == 3


# =============================================================================
# Bloom's Verb Validation Tests (Mocked)
# =============================================================================

class TestArchitectBloomValidation:
    """Test suite for Bloom's verb validation in Architect."""

    @patch('src.modules.architect.dspy.Predict.forward')
    def test_valid_blooms_verbs_pass_validation(self, mock_forward, mock_architect_response):
        """Test that valid Bloom's verbs pass validation."""
        mock_prediction = Mock()
        mock_prediction.course_structure = mock_architect_response
        mock_forward.return_value = mock_prediction

        architect = Architect()
        result = architect.generate_objectives(
            topic="Test Topic",
            target_audience="Test Audience",
            num_objectives=3,
        )

        # Should not raise assertion error
        assert len(result.objectives) == 3

    @patch('src.modules.architect.dspy.Predict.forward')
    def test_invalid_blooms_verb_fails_validation(self, mock_forward, mock_invalid_verb_response):
        """Test that invalid Bloom's verb fails validation."""
        mock_prediction = Mock()
        mock_prediction.course_structure = mock_invalid_verb_response
        mock_forward.return_value = mock_prediction

        architect = Architect()

        with pytest.raises(AssertionError) as exc_info:
            architect.generate_objectives(
                topic="Test Topic",
                target_audience="Test Audience",
                num_objectives=1,
            )

        assert "Bloom's verb validation failed" in str(exc_info.value)

    @patch('src.modules.architect.dspy.Predict.forward')
    def test_validate_all_objectives_use_approved_verbs(self, mock_forward, mock_architect_response):
        """Test that all objectives use approved Bloom's verbs."""
        mock_prediction = Mock()
        mock_prediction.course_structure = mock_architect_response
        mock_forward.return_value = mock_prediction

        architect = Architect()
        result = architect.generate_objectives(
            topic="Test Topic",
            target_audience="Test Audience",
            num_objectives=3,
        )

        # Verify each objective uses approved verb
        from src.core.models import BloomsTaxonomy
        for objective in result.objectives:
            level_str = objective.level.value
            assert BloomsTaxonomy.validate_verb(objective.verb, level_str), \
                f"Verb '{objective.verb}' not valid for level '{level_str}'"


# =============================================================================
# Objective Count Validation Tests
# =============================================================================

class TestArchitectCountValidation:
    """Test suite for objective count validation."""

    @patch('src.modules.architect.dspy.Predict.forward')
    def test_correct_objective_count_passes(self, mock_forward, mock_architect_response):
        """Test that correct objective count passes validation."""
        mock_prediction = Mock()
        mock_prediction.course_structure = mock_architect_response
        mock_forward.return_value = mock_prediction

        architect = Architect()
        result = architect.generate_objectives(
            topic="Test Topic",
            target_audience="Test Audience",
            num_objectives=3,
        )

        # Should pass validation
        assert len(result.objectives) == 3

    @patch('src.modules.architect.dspy.Predict.forward')
    def test_wrong_objective_count_fails(self, mock_forward, mock_wrong_count_response):
        """Test that wrong objective count fails validation."""
        mock_prediction = Mock()
        mock_prediction.course_structure = mock_wrong_count_response
        mock_forward.return_value = mock_prediction

        architect = Architect()

        with pytest.raises(ValueError) as exc_info:
            architect.generate_objectives(
                topic="Test Topic",
                target_audience="Test Audience",
                num_objectives=3,  # Requested 3
            )

        assert "Expected 3 objectives, got 1" in str(exc_info.value)


# =============================================================================
# Error Handling Tests (Mocked)
# =============================================================================

class TestArchitectErrorHandling:
    """Test suite for error handling with mocked failures."""

    @patch('src.modules.architect.dspy.Predict.forward')
    def test_handles_json_parsing_error(self, mock_forward):
        """Test handling of JSON parsing errors."""
        # Mock response that causes parsing error
        mock_forward.side_effect = json.JSONDecodeError("test", "{}", 0)

        architect = Architect()

        with pytest.raises(json.JSONDecodeError):
            architect.generate_objectives(
                topic="Test Topic",
                target_audience="Test Audience",
                num_objectives=3,
            )

    @patch('src.modules.architect.dspy.Predict.forward')
    def test_handles_validation_error(self, mock_forward):
        """Test handling of Pydantic validation errors."""
        from pydantic import ValidationError

        # Mock response with invalid data
        invalid_response = {
            "topic": "Test",
            "objectives": []  # Empty objectives (invalid)
        }
        mock_prediction = Mock()
        mock_prediction.course_structure = invalid_response
        mock_forward.return_value = mock_prediction

        architect = Architect()

        with pytest.raises(ValidationError):
            architect.generate_objectives(
                topic="Test Topic",
                target_audience="Test Audience",
                num_objectives=3,
            )

    @patch('src.modules.architect.dspy.Predict.forward')
    def test_handles_llm_failure(self, mock_forward):
        """Test handling of LLM failure."""
        mock_forward.side_effect = Exception("LLM unavailable")

        architect = Architect()

        with pytest.raises(Exception) as exc_info:
            architect.generate_objectives(
                topic="Test Topic",
                target_audience="Test Audience",
                num_objectives=3,
            )

        assert "LLM unavailable" in str(exc_info.value)


# =============================================================================
# Prompt Logic Tests
# =============================================================================

class TestArchitectPromptLogic:
    """Test suite for prompt logic verification."""

    @patch('src.modules.architect.dspy.Predict.forward')
    def test_prompt_contains_topic(self, mock_forward, mock_architect_response):
        """Test that prompt includes topic parameter."""
        mock_prediction = Mock()
        mock_prediction.course_structure = mock_architect_response
        mock_forward.return_value = mock_prediction

        architect = Architect()
        architect.generate_objectives(
            topic="Machine Learning Fundamentals",
            target_audience="Developers",
            num_objectives=3,
        )

        # Verify forward was called with topic
        call_args = mock_forward.call_args
        assert call_args[1]['topic'] == "Machine Learning Fundamentals"

    @patch('src.modules.architect.dspy.Predict.forward')
    def test_prompt_contains_target_audience(self, mock_forward, mock_architect_response):
        """Test that prompt includes target_audience parameter."""
        mock_prediction = Mock()
        mock_prediction.course_structure = mock_architect_response
        mock_forward.return_value = mock_prediction

        architect = Architect()
        architect.generate_objectives(
            topic="Test Topic",
            target_audience="Data Scientists",
            num_objectives=3,
        )

        # Verify forward was called with target_audience
        call_args = mock_forward.call_args
        assert call_args[1]['target_audience'] == "Data Scientists"

    @patch('src.modules.architect.dspy.Predict.forward')
    def test_prompt_contains_num_objectives(self, mock_forward, mock_architect_response):
        """Test that prompt includes num_objectives parameter."""
        mock_prediction = Mock()
        # Create response with 8 objectives to match the request
        eight_objectives_response = {
            "topic": "Test Topic",
            "objectives": [
                {
                    "id": f"LO-{i:03d}",
                    "verb": "explain",
                    "content": f"test content {i}",
                    "level": "Understand"
                }
                for i in range(1, 9)  # 8 objectives
            ]
        }
        mock_prediction.course_structure = eight_objectives_response
        mock_forward.return_value = mock_prediction

        architect = Architect()
        architect.generate_objectives(
            topic="Test Topic",
            target_audience="Test Audience",
            num_objectives=8,
        )

        # Verify forward was called with num_objectives
        call_args = mock_forward.call_args
        assert call_args[1]['num_objectives'] == 8


# =============================================================================
# Edge Cases with Mocks
# =============================================================================

class TestArchitectEdgeCases:
    """Test suite for edge cases with mocked scenarios."""

    @patch('src.modules.architect.dspy.Predict.forward')
    def test_generate_single_objective(self, mock_forward):
        """Test generating just 1 objective."""
        response = {
            "topic": "Test Topic",
            "objectives": [
                {
                    "id": "LO-001",
                    "verb": "define",
                    "content": "test",
                    "level": "Remember"
                }
            ]
        }
        mock_prediction = Mock()
        mock_prediction.course_structure = response
        mock_forward.return_value = mock_prediction

        architect = Architect()
        result = architect.generate_objectives(
            topic="Test Topic",
            target_audience="Test Audience",
            num_objectives=1,
        )

        assert len(result.objectives) == 1

    @patch('src.modules.architect.dspy.Predict.forward')
    def test_generate_many_objectives(self, mock_forward):
        """Test generating 12 objectives (maximum)."""
        objectives = []
        for i in range(12):
            objectives.append({
                "id": f"LO-{i+1:03d}",
                "verb": "explain",
                "content": f"test content {i+1}",
                "level": "Understand"
            })

        response = {
            "topic": "Test Topic",
            "objectives": objectives
        }
        mock_prediction = Mock()
        mock_prediction.course_structure = response
        mock_forward.return_value = mock_prediction

        architect = Architect()
        result = architect.generate_objectives(
            topic="Test Topic",
            target_audience="Test Audience",
            num_objectives=12,
        )

        assert len(result.objectives) == 12

    @patch('src.modules.architect.dspy.Predict.forward')
    def test_all_bloom_levels_present(self, mock_forward):
        """Test that all 6 Bloom's levels are represented."""
        response = {
            "topic": "Test Topic",
            "objectives": [
                {"id": "LO-001", "verb": "define", "content": "test", "level": "Remember"},
                {"id": "LO-002", "verb": "explain", "content": "test", "level": "Understand"},
                {"id": "LO-003", "verb": "apply", "content": "test", "level": "Apply"},
                {"id": "LO-004", "verb": "analyze", "content": "test", "level": "Analyze"},
                {"id": "LO-005", "verb": "evaluate", "content": "test", "level": "Evaluate"},
                {"id": "LO-006", "verb": "create", "content": "test", "level": "Create"},
            ]
        }
        mock_prediction = Mock()
        mock_prediction.course_structure = response
        mock_forward.return_value = mock_prediction

        architect = Architect()
        result = architect.generate_objectives(
            topic="Test Topic",
            target_audience="Test Audience",
            num_objectives=6,
        )

        levels = [obj.level for obj in result.objectives]
        assert BloomLevel.REMEMBER in levels
        assert BloomLevel.UNDERSTAND in levels
        assert BloomLevel.APPLY in levels
        assert BloomLevel.ANALYZE in levels
        assert BloomLevel.EVALUATE in levels
        assert BloomLevel.CREATE in levels

    @patch('src.modules.architect.dspy.Predict.forward')
    def test_special_characters_in_topic(self, mock_forward):
        """Test handling special characters in topic."""
        response = {
            "topic": "Python & Django: Web Development! (2024)",
            "objectives": [
                {"id": "LO-001", "verb": "define", "content": "test", "level": "Remember"}
            ]
        }
        mock_prediction = Mock()
        mock_prediction.course_structure = response
        mock_forward.return_value = mock_prediction

        architect = Architect()
        result = architect.generate_objectives(
            topic="Python & Django: Web Development! (2024)",
            target_audience="Test Audience",
            num_objectives=1,
        )

        assert "&" in result.topic
        assert "!" in result.topic


# =============================================================================
# Signature Tests
# =============================================================================

class TestGenerateObjectivesSignature:
    """Test suite for GenerateObjectives DSPy signature."""

    def test_signature_has_input_fields(self):
        """Test that signature has required input fields."""
        # DSPy signatures store fields as class attributes
        assert 'topic' in GenerateObjectives.__annotations__ or hasattr(GenerateObjectives, 'topic')
        assert 'target_audience' in GenerateObjectives.__annotations__ or hasattr(GenerateObjectives, 'target_audience')
        assert 'num_objectives' in GenerateObjectives.__annotations__ or hasattr(GenerateObjectives, 'num_objectives')

    def test_signature_has_output_field(self):
        """Test that signature has course_structure output field."""
        assert 'course_structure' in GenerateObjectives.__annotations__ or hasattr(GenerateObjectives, 'course_structure')
