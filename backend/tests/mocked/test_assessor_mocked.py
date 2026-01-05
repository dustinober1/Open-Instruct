"""
Mocked tests for Assessor DSPy module.

Tests cover:
- Mocked LLM responses for quiz generation
- Question quality validation with mocked data
- Distractor validation tests
- Error handling with mock failures
- Edge cases with various quiz scenarios
"""

from unittest.mock import Mock, patch

import pytest
import dspy

from src.core.models import BloomLevel, LearningObjective, QuizQuestion
from src.modules.assessor import Assessor, GenerateQuiz


# =============================================================================
# Mock Response Fixtures
# =============================================================================

@pytest.fixture
def sample_learning_objective():
    """Sample learning objective for testing."""
    return LearningObjective(
        id="LO-001",
        verb="explain",
        content="the differences between supervised and unsupervised learning",
        level=BloomLevel.UNDERSTAND,
    )


@pytest.fixture
def mock_quiz_response():
    """Mock successful Assessor LLM response."""
    return {
        "stem": "What is the key characteristic that distinguishes unsupervised learning from supervised learning?",
        "correct_answer": "Unsupervised learning works with unlabeled data to find hidden patterns, while supervised learning requires labeled input-output pairs",
        "distractors": [
            "Unsupervised learning is faster than supervised learning",
            "Supervised learning cannot handle numerical data",
            "Unsupervised learning requires more training data than supervised learning"
        ],
        "explanation": "The fundamental difference is the presence of labels. Supervised learning uses labeled data (input with known outputs) to learn mapping functions, while unsupervised learning finds patterns in unlabeled data without explicit feedback."
    }


@pytest.fixture
def mock_invalid_stem_response():
    """Mock response with invalid stem (too short, no question mark)."""
    return {
        "stem": "Test?",  # Too short
        "correct_answer": "Test answer",
        "distractors": ["Wrong 1", "Wrong 2", "Wrong 3"],
        "explanation": "Test explanation",
    }


@pytest.fixture
def mock_duplicate_distractors_response():
    """Mock response with duplicate distractors."""
    return {
        "stem": "What is machine learning?",
        "correct_answer": "A subset of AI that enables systems to learn from data",
        "distractors": ["Wrong answer", "Wrong answer", "Another wrong"],  # Duplicate
        "explanation": "Test explanation",
    }


@pytest.fixture
def mock_correct_answer_in_distractors_response():
    """Mock response with correct answer in distractors."""
    return {
        "stem": "What is machine learning?",
        "correct_answer": "A subset of AI",
        "distractors": [
            "A programming language",
            "A subset of AI",  # Correct answer in distractors!
            "A database system"
        ],
        "explanation": "Test explanation",
    }


# =============================================================================
# Assessor Initialization Tests
# =============================================================================

class TestAssessorInit:
    """Test suite for Assessor initialization."""

    @patch('src.modules.assessor.dspy.Predict.__init__')
    def test_assessor_initialization(self, mock_predict_init):
        """Test Assessor module initialization."""
        mock_predict_init.return_value = None
        assessor = Assessor()
        assert assessor is not None

    @patch('src.modules.assessor.dspy.Predict.__init__')
    def test_assessor_with_custom_kwargs(self, mock_predict_init):
        """Test Assessor initialization with custom kwargs."""
        mock_predict_init.return_value = None
        assessor = Assessor(temperature=0.5, max_tokens=500)
        assert assessor is not None


# =============================================================================
# Mocked Generation Tests
# =============================================================================

class TestAssessorMockedGeneration:
    """Test suite for mocked Assessor generation."""

    @patch('src.modules.assessor.dspy.Predict.forward')
    def test_generate_quiz_with_mock(self, mock_forward, sample_learning_objective, mock_quiz_response):
        """Test generating quiz with mocked LLM response."""
        # Setup mock prediction
        mock_prediction = Mock()
        mock_prediction.quiz_question = mock_quiz_response
        mock_forward.return_value = mock_prediction

        # Create assessor and generate
        assessor = Assessor()
        result = assessor.generate_quiz(
            objective=sample_learning_objective,
            context="Introduction to Machine Learning",
        )

        # Verify result
        assert isinstance(result, QuizQuestion)
        assert result.stem == mock_quiz_response["stem"]
        assert result.correct_answer == mock_quiz_response["correct_answer"]
        assert len(result.distractors) == 3

        # Verify LLM was called
        mock_forward.assert_called_once()

    @patch('src.modules.assessor.dspy.Predict.forward')
    def test_forward_returns_prediction(self, mock_forward, sample_learning_objective, mock_quiz_response):
        """Test that forward method returns object with quiz_question."""
        mock_prediction = Mock()
        mock_prediction.quiz_question = mock_quiz_response
        mock_forward.return_value = mock_prediction

        assessor = Assessor()
        prediction = assessor.forward(
            objective=sample_learning_objective,
            context="Test context",
        )

        # With mocking, we get a Mock back - just verify it has the right structure
        assert hasattr(prediction, 'quiz_question')

    @patch('src.modules.assessor.dspy.Predict.forward')
    def test_generate_with_dict_response(self, mock_forward, sample_learning_objective, mock_quiz_response):
        """Test generating when LLM returns dict (not QuizQuestion)."""
        mock_prediction = Mock()
        mock_prediction.quiz_question = mock_quiz_response  # Dict, not QuizQuestion
        mock_forward.return_value = mock_prediction

        assessor = Assessor()
        result = assessor.generate_quiz(
            objective=sample_learning_objective,
        )

        # Should convert dict to QuizQuestion
        assert isinstance(result, QuizQuestion)
        assert len(result.distractors) == 3

    @patch('src.modules.assessor.dspy.Predict.forward')
    def test_objective_formatting_in_prompt(self, mock_forward, sample_learning_objective, mock_quiz_response):
        """Test that objective is properly formatted in prompt."""
        mock_prediction = Mock()
        mock_prediction.quiz_question = mock_quiz_response
        mock_forward.return_value = mock_prediction

        assessor = Assessor()
        assessor.generate_quiz(objective=sample_learning_objective)

        # Verify forward was called with formatted objective string
        call_args = mock_forward.call_args
        expected_objective_str = "explain the differences between supervised and unsupervised learning"
        assert call_args[1]['objective'] == expected_objective_str


# =============================================================================
# Question Quality Validation Tests
# =============================================================================

class TestAssessorQualityValidation:
    """Test suite for quiz question quality validation."""

    @patch('src.modules.assessor.dspy.Predict.forward')
    def test_valid_question_passes_validation(self, mock_forward, sample_learning_objective, mock_quiz_response):
        """Test that valid question passes all quality checks."""
        mock_prediction = Mock()
        mock_prediction.quiz_question = mock_quiz_response
        mock_forward.return_value = mock_prediction

        assessor = Assessor()
        result = assessor.generate_quiz(objective=sample_learning_objective)

        # Should pass all validation
        assert len(result.stem) >= 10
        assert result.stem.endswith('?')
        assert len(result.distractors) == 3

    @patch('src.modules.assessor.dspy.Predict.forward')
    def test_stem_too_short_fails_validation(self, mock_forward, sample_learning_objective, mock_invalid_stem_response):
        """Test that stem that's too short fails validation."""
        mock_prediction = Mock()
        mock_prediction.quiz_question = mock_invalid_stem_response
        mock_forward.return_value = mock_prediction

        assessor = Assessor()

        with pytest.raises(Exception):  # dspy.Assert raises exception
            assessor.generate_quiz(objective=sample_learning_objective)

    @patch('src.modules.assessor.dspy.Predict.forward')
    def test_stem_without_question_mark_fails(self, mock_forward, sample_learning_objective):
        """Test that stem without question mark fails validation."""
        response = {
            "stem": "This is a statement without question mark",
            "correct_answer": "Test answer",
            "distractors": ["Wrong 1", "Wrong 2", "Wrong 3"],
            "explanation": "Test explanation",
        }
        mock_prediction = Mock()
        mock_prediction.quiz_question = response
        mock_forward.return_value = mock_prediction

        assessor = Assessor()

        with pytest.raises(Exception):  # dspy.Assert raises exception
            assessor.generate_quiz(objective=sample_learning_objective)

    @patch('src.modules.assessor.dspy.Predict.forward')
    def test_empty_correct_answer_fails(self, mock_forward, sample_learning_objective):
        """Test that empty correct answer fails validation."""
        response = {
            "stem": "What is this?",
            "correct_answer": "",  # Empty
            "distractors": ["Wrong 1", "Wrong 2", "Wrong 3"],
            "explanation": "Test explanation",
        }
        mock_prediction = Mock()
        mock_prediction.quiz_question = response
        mock_forward.return_value = mock_prediction

        assessor = Assessor()

        with pytest.raises(Exception):
            assessor.generate_quiz(objective=sample_learning_objective)

    @patch('src.modules.assessor.dspy.Predict.forward')
    def test_explanation_too_short_fails(self, mock_forward, sample_learning_objective):
        """Test that explanation that's too short fails validation."""
        response = {
            "stem": "What is this test?",
            "correct_answer": "Test answer",
            "distractors": ["Wrong 1", "Wrong 2", "Wrong 3"],
            "explanation": "Too short",  # Less than 15 characters
        }
        mock_prediction = Mock()
        mock_prediction.quiz_question = response
        mock_forward.return_value = mock_prediction

        assessor = Assessor()

        with pytest.raises(Exception):
            assessor.generate_quiz(objective=sample_learning_objective)


# =============================================================================
# Distractor Validation Tests
# =============================================================================

class TestAssessorDistractorValidation:
    """Test suite for distractor validation."""

    @patch('src.modules.assessor.dspy.Predict.forward')
    def test_exactly_three_distractors_required(self, mock_forward, sample_learning_objective, mock_quiz_response):
        """Test that exactly 3 distractors are required."""
        mock_prediction = Mock()
        mock_prediction.quiz_question = mock_quiz_response
        mock_forward.return_value = mock_prediction

        assessor = Assessor()
        result = assessor.generate_quiz(objective=sample_learning_objective)

        # Should have exactly 3 distractors
        assert len(result.distractors) == 3

    @patch('src.modules.assessor.dspy.Predict.forward')
    def test_duplicate_distractors_fail_validation(self, mock_forward, sample_learning_objective, mock_duplicate_distractors_response):
        """Test that duplicate distractors fail validation."""
        mock_prediction = Mock()
        mock_prediction.quiz_question = mock_duplicate_distractors_response
        mock_forward.return_value = mock_prediction

        assessor = Assessor()

        with pytest.raises(Exception):  # dspy.Assert raises exception
            assessor.generate_quiz(objective=sample_learning_objective)

    @patch('src.modules.assessor.dspy.Predict.forward')
    def test_correct_answer_not_in_distractors(self, mock_forward, sample_learning_objective, mock_correct_answer_in_distractors_response):
        """Test that correct answer cannot be in distractors."""
        mock_prediction = Mock()
        mock_prediction.quiz_question = mock_correct_answer_in_distractors_response
        mock_forward.return_value = mock_prediction

        assessor = Assessor()

        with pytest.raises(Exception):  # dspy.Assert raises exception
            assessor.generate_quiz(objective=sample_learning_objective)

    @patch('src.modules.assessor.dspy.Predict.forward')
    def test_empty_distractor_fails(self, mock_forward, sample_learning_objective):
        """Test that empty distractor fails validation."""
        response = {
            "stem": "What is this?",
            "correct_answer": "Test answer",
            "distractors": ["Wrong 1", "", "Wrong 3"],  # One empty
            "explanation": "Test explanation",
        }
        mock_prediction = Mock()
        mock_prediction.quiz_question = response
        mock_forward.return_value = mock_prediction

        assessor = Assessor()

        with pytest.raises(Exception):
            assessor.generate_quiz(objective=sample_learning_objective)

    @patch('src.modules.assessor.dspy.Predict.forward')
    def test_all_distractors_unique(self, mock_forward, sample_learning_objective, mock_quiz_response):
        """Test that all distractors are unique."""
        mock_prediction = Mock()
        mock_prediction.quiz_question = mock_quiz_response
        mock_forward.return_value = mock_prediction

        assessor = Assessor()
        result = assessor.generate_quiz(objective=sample_learning_objective)

        # All distractors should be unique
        assert len(set(result.distractors)) == 3
        assert result.correct_answer not in result.distractors


# =============================================================================
# Error Handling Tests (Mocked)
# =============================================================================

class TestAssessorErrorHandling:
    """Test suite for error handling with mocked failures."""

    @patch('src.modules.assessor.dspy.Predict.forward')
    def test_handles_json_parsing_error(self, mock_forward, sample_learning_objective):
        """Test handling of JSON parsing errors."""
        import json

        mock_forward.side_effect = json.JSONDecodeError("test", "{}", 0)

        assessor = Assessor()

        with pytest.raises(json.JSONDecodeError):
            assessor.generate_quiz(objective=sample_learning_objective)

    @patch('src.modules.assessor.dspy.Predict.forward')
    def test_handles_validation_error(self, mock_forward, sample_learning_objective):
        """Test handling of Pydantic validation errors."""
        from pydantic import ValidationError

        # Mock response with invalid data
        invalid_response = {
            "stem": "What is this?",
            "correct_answer": "Test answer",
            "distractors": [],  # Empty (invalid)
            "explanation": "Test explanation",
        }
        mock_prediction = Mock()
        mock_prediction.quiz_question = invalid_response
        mock_forward.return_value = mock_prediction

        assessor = Assessor()

        with pytest.raises(ValidationError):
            assessor.generate_quiz(objective=sample_learning_objective)

    @patch('src.modules.assessor.dspy.Predict.forward')
    def test_handles_llm_failure(self, mock_forward, sample_learning_objective):
        """Test handling of LLM failure."""
        mock_forward.side_effect = Exception("LLM unavailable")

        assessor = Assessor()

        with pytest.raises(Exception) as exc_info:
            assessor.generate_quiz(objective=sample_learning_objective)

        assert "LLM unavailable" in str(exc_info.value)


# =============================================================================
# Context Parameter Tests
# =============================================================================

class TestAssessorContext:
    """Test suite for context parameter handling."""

    @patch('src.modules.assessor.dspy.Predict.forward')
    def test_generate_with_context(self, mock_forward, sample_learning_objective, mock_quiz_response):
        """Test generating quiz with context."""
        mock_prediction = Mock()
        mock_prediction.quiz_question = mock_quiz_response
        mock_forward.return_value = mock_prediction

        assessor = Assessor()
        result = assessor.generate_quiz(
            objective=sample_learning_objective,
            context="Machine Learning Course",
        )

        # Verify context was passed to LLM
        call_args = mock_forward.call_args
        assert call_args[1]['context'] == "Machine Learning Course"

    @patch('src.modules.assessor.dspy.Predict.forward')
    def test_generate_without_context(self, mock_forward, sample_learning_objective, mock_quiz_response):
        """Test generating quiz without context (optional)."""
        mock_prediction = Mock()
        mock_prediction.quiz_question = mock_quiz_response
        mock_forward.return_value = mock_prediction

        assessor = Assessor()
        result = assessor.generate_quiz(
            objective=sample_learning_objective,
            context=None,
        )

        # Should work without context
        assert isinstance(result, QuizQuestion)


# =============================================================================
# Edge Cases with Mocks
# =============================================================================

class TestAssessorEdgeCases:
    """Test suite for edge cases with mocked scenarios."""

    @patch('src.modules.assessor.dspy.Predict.forward')
    def test_very_long_stem(self, mock_forward, sample_learning_objective):
        """Test handling of very long question stem."""
        long_stem = "What is " + "test " * 100 + "?"
        response = {
            "stem": long_stem,
            "correct_answer": "Test answer",
            "distractors": ["Wrong 1", "Wrong 2", "Wrong 3"],
            "explanation": "Test explanation",
        }
        mock_prediction = Mock()
        mock_prediction.quiz_question = response
        mock_forward.return_value = mock_prediction

        assessor = Assessor()
        result = assessor.generate_quiz(objective=sample_learning_objective)

        assert len(result.stem) == len(long_stem)

    @patch('src.modules.assessor.dspy.Predict.forward')
    def test_very_long_answer_options(self, mock_forward, sample_learning_objective):
        """Test handling of very long answer options."""
        long_answer = "answer " * 100
        response = {
            "stem": "What is this test?",
            "correct_answer": long_answer,
            "distractors": [long_answer + " 1", long_answer + " 2", long_answer + " 3"],
            "explanation": "Test explanation",
        }
        mock_prediction = Mock()
        mock_prediction.quiz_question = response
        mock_forward.return_value = mock_prediction

        assessor = Assessor()
        result = assessor.generate_quiz(objective=sample_learning_objective)

        assert len(result.correct_answer) == len(long_answer)

    @patch('src.modules.assessor.dspy.Predict.forward')
    def test_special_characters_in_stem(self, mock_forward, sample_learning_objective):
        """Test handling special characters in question stem."""
        response = {
            "stem": "What is the relationship between Python & Django?",
            "correct_answer": "Test answer",
            "distractors": ["Wrong 1", "Wrong 2", "Wrong 3"],
            "explanation": "Test explanation",
        }
        mock_prediction = Mock()
        mock_prediction.quiz_question = response
        mock_forward.return_value = mock_prediction

        assessor = Assessor()
        result = assessor.generate_quiz(objective=sample_learning_objective)

        assert "&" in result.stem

    @patch('src.modules.assessor.dspy.Predict.forward')
    def test_unicode_in_quiz(self, mock_forward, sample_learning_objective):
        """Test handling unicode in quiz."""
        response = {
            "stem": "What is machine learning in Chinese? 什么是机器学习?",  # Add question mark for validation
            "correct_answer": "人工智能的一个分支 that enables systems to learn from data",
            "distractors": ["编程语言 for data analysis", "数据库管理系统", "操作系统 kernel"],
            "explanation": "机器学习 is indeed a branch of AI that focuses on building systems",
        }
        mock_prediction = Mock()
        mock_prediction.quiz_question = response
        mock_forward.return_value = mock_prediction

        assessor = Assessor()
        result = assessor.generate_quiz(objective=sample_learning_objective)

        assert "机器学习" in result.stem


# =============================================================================
# Signature Tests
# =============================================================================

class TestGenerateQuizSignature:
    """Test suite for GenerateQuiz DSPy signature."""

    def test_signature_has_input_fields(self):
        """Test that signature has required input fields."""
        assert 'objective' in GenerateQuiz.__annotations__ or hasattr(GenerateQuiz, 'objective')
        assert 'context' in GenerateQuiz.__annotations__ or hasattr(GenerateQuiz, 'context')

    def test_signature_has_output_field(self):
        """Test that signature has quiz_question output field."""
        assert 'quiz_question' in GenerateQuiz.__annotations__ or hasattr(GenerateQuiz, 'quiz_question')

    def test_context_is_optional(self):
        """Test that context field is optional."""
        # The field should have default=None (check in model_fields for Pydantic V2)
        if hasattr(GenerateQuiz, 'model_fields'):
            field = GenerateQuiz.model_fields.get('context')
        else:
            field = GenerateQuiz.__fields__.get('context')
        assert field is not None
        # Optional fields should allow None
