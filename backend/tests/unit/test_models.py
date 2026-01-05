"""
Unit tests for Pydantic models in core/models.py.

Tests cover:
- Valid inputs for all models
- Invalid inputs and validation errors
- Edge cases and boundary conditions
- Field validators
- Custom validation logic
"""

import pytest
from pydantic import ValidationError

from src.core.models import (
    BloomLevel,
    BloomsTaxonomy,
    CourseStructure,
    LearningObjective,
    QuizQuestion,
)


# =============================================================================
# Learning Objective Tests
# =============================================================================

class TestLearningObjective:
    """Test suite for LearningObjective model."""

    def test_valid_learning_objective(self, valid_learning_objective_data):
        """Test creating a valid LearningObjective."""
        objective = LearningObjective(**valid_learning_objective_data)
        assert objective.id == "LO-001"
        assert objective.verb == "explain"
        assert objective.content == "the core concepts of machine learning"
        assert objective.level == BloomLevel.UNDERSTAND

    def test_learning_objective_missing_required_field(self):
        """Test that missing required fields raise ValidationError."""
        with pytest.raises(ValidationError) as exc_info:
            LearningObjective(
                id="LO-001",
                verb="explain",
                # Missing 'content'
                level=BloomLevel.UNDERSTAND,
            )
        errors = exc_info.value.errors()
        assert any(e["loc"] == ("content",) for e in errors)

    def test_learning_objective_with_empty_content(self):
        """Test that empty content is rejected."""
        with pytest.raises(ValidationError):
            LearningObjective(
                id="LO-001",
                verb="explain",
                content="",
                level=BloomLevel.UNDERSTAND,
            )

    def test_learning_objective_with_empty_verb(self):
        """Test that empty verb is rejected."""
        with pytest.raises(ValidationError):
            LearningObjective(
                id="LO-001",
                verb="",
                content="test content",
                level=BloomLevel.UNDERSTAND,
            )

    def test_learning_objective_all_bloom_levels(self):
        """Test creating objectives with all Bloom's levels."""
        for level in BloomLevel:
            objective = LearningObjective(
                id=f"LO-{level.value}",
                verb="test",
                content="test content",
                level=level,
            )
            assert objective.level == level

    @pytest.mark.parametrize("invalid_id", ["", "lo-001", "LO001", "LO_001", "LO-"])
    def test_learning_objective_invalid_id_formats(self, invalid_id):
        """Test various invalid ID formats."""
        # Note: Current model doesn't enforce ID format, so this tests current behavior
        # If ID validation is added, these should fail
        objective = LearningObjective(
            id=invalid_id,
            verb="test",
            content="test content",
            level=BloomLevel.UNDERSTAND,
        )
        assert objective.id == invalid_id


# =============================================================================
# Course Structure Tests
# =============================================================================

class TestCourseStructure:
    """Test suite for CourseStructure model."""

    def test_valid_course_structure(self, valid_course_structure_data):
        """Test creating a valid CourseStructure."""
        structure = CourseStructure(**valid_course_structure_data)
        assert structure.topic == "Introduction to Machine Learning"
        assert len(structure.objectives) == 3

    def test_course_structure_with_empty_objectives_list(self):
        """Test that empty objectives list raises ValidationError."""
        with pytest.raises(ValidationError) as exc_info:
            CourseStructure(
                topic="Test Topic",
                objectives=[],
            )
        errors = exc_info.value.errors()
        assert any("at least 1" in str(e).lower() for e in errors)

    def test_course_structure_with_single_objective(self):
        """Test course structure with minimum objectives (1)."""
        objective = LearningObjective(
            id="LO-001",
            verb="explain",
            content="test content",
            level=BloomLevel.UNDERSTAND,
        )
        structure = CourseStructure(
            topic="Test Topic",
            objectives=[objective],
        )
        assert len(structure.objectives) == 1

    def test_course_structure_with_many_objectives(self, sample_learning_objectives):
        """Test course structure with multiple objectives."""
        structure = CourseStructure(
            topic="Test Topic",
            objectives=sample_learning_objectives,
        )
        assert len(structure.objectives) == 6

    def test_course_structure_with_invalid_objective(self):
        """Test that invalid objective in list raises ValidationError."""
        with pytest.raises(ValidationError):
            CourseStructure(
                topic="Test Topic",
                objectives=[
                    {
                        "id": "LO-001",
                        "verb": "explain",
                        # Missing 'content' and 'level'
                    }
                ],
            )

    def test_course_structure_topic_validation(self):
        """Test topic field validation."""
        # Empty topic
        with pytest.raises(ValidationError):
            CourseStructure(
                topic="",
                objectives=[
                    LearningObjective(
                        id="LO-001",
                        verb="test",
                        content="test",
                        level=BloomLevel.REMEMBER,
                    )
                ],
            )

        # Whitespace-only topic
        with pytest.raises(ValidationError):
            CourseStructure(
                topic="   ",
                objectives=[
                    LearningObjective(
                        id="LO-001",
                        verb="test",
                        content="test",
                        level=BloomLevel.REMEMBER,
                    )
                ],
            )


# =============================================================================
# Quiz Question Tests
# =============================================================================

class TestQuizQuestion:
    """Test suite for QuizQuestion model."""

    def test_valid_quiz_question(self, valid_quiz_question_data):
        """Test creating a valid QuizQuestion."""
        question = QuizQuestion(**valid_quiz_question_data)
        assert question.stem == valid_quiz_question_data["stem"]
        assert question.correct_answer == valid_quiz_question_data["correct_answer"]
        assert len(question.distractors) == 3
        assert question.explanation == valid_quiz_question_data["explanation"]

    def test_quiz_question_distractor_count_validation(self):
        """Test that exactly 3 distractors are required."""
        # Too few distractors
        with pytest.raises(ValidationError) as exc_info:
            QuizQuestion(
                stem="What is test?",
                correct_answer="Test answer",
                distractors=["Wrong 1", "Wrong 2"],  # Only 2
                explanation="Test explanation",
            )
        assert "at least 3 items" in str(exc_info.value).lower() or "Exactly 3 distractors required" in str(exc_info.value)

        # Too many distractors
        with pytest.raises(ValidationError) as exc_info:
            QuizQuestion(
                stem="What is test?",
                correct_answer="Test answer",
                distractors=["Wrong 1", "Wrong 2", "Wrong 3", "Wrong 4"],  # 4
                explanation="Test explanation",
            )
        assert "at most 3 items" in str(exc_info.value).lower()

    def test_quiz_question_unique_distractors_validation(self):
        """Test that distractors must be unique."""
        with pytest.raises(ValidationError) as exc_info:
            QuizQuestion(
                stem="What is test?",
                correct_answer="Test answer",
                distractors=["Wrong 1", "Wrong 1", "Wrong 2"],  # Duplicate
                explanation="Test explanation",
            )
        assert "Distractors must be unique" in str(exc_info.value)

    def test_quiz_question_distractor_not_in_correct_answer(self):
        """Test that correct answer cannot appear in distractors."""
        with pytest.raises(ValidationError) as exc_info:
            QuizQuestion(
                stem="What is test?",
                correct_answer="Test answer",
                distractors=["Test answer", "Wrong 1", "Wrong 2"],  # Correct answer in distractors
                explanation="Test explanation",
            )
        assert "Distractors must not contain correct_answer" in str(exc_info.value)

    def test_quiz_question_empty_stem(self):
        """Test that empty stem is rejected."""
        with pytest.raises(ValidationError):
            QuizQuestion(
                stem="",
                correct_answer="Test answer",
                distractors=["Wrong 1", "Wrong 2", "Wrong 3"],
                explanation="Test explanation",
            )

    def test_quiz_question_empty_correct_answer(self):
        """Test that empty correct answer is rejected."""
        with pytest.raises(ValidationError):
            QuizQuestion(
                stem="What is test?",
                correct_answer="",
                distractors=["Wrong 1", "Wrong 2", "Wrong 3"],
                explanation="Test explanation",
            )

    def test_quiz_question_empty_distractor(self):
        """Test that empty distractors are rejected."""
        with pytest.raises(ValidationError):
            QuizQuestion(
                stem="What is test?",
                correct_answer="Test answer",
                distractors=["Wrong 1", "", "Wrong 3"],  # One empty distractor
                explanation="Test explanation",
            )

    def test_quiz_question_empty_explanation(self):
        """Test that empty explanation is rejected."""
        with pytest.raises(ValidationError):
            QuizQuestion(
                stem="What is test?",
                correct_answer="Test answer",
                distractors=["Wrong 1", "Wrong 2", "Wrong 3"],
                explanation="",
            )

    @pytest.mark.parametrize("stem", [
        "This is a statement",  # No question mark
        "Is this a question",  # No question mark
        "Question!",  # Exclamation mark instead
    ])
    def test_quiz_question_stem_without_question_mark(self, stem):
        """Test that stems without question marks are accepted (current behavior)."""
        # Note: Current model doesn't enforce question mark, this tests current behavior
        question = QuizQuestion(
            stem=stem,
            correct_answer="Test answer",
            distractors=["Wrong 1", "Wrong 2", "Wrong 3"],
            explanation="Test explanation",
        )
        assert question.stem == stem


# =============================================================================
# BloomsTaxonomy Class Tests
# =============================================================================

class TestBloomsTaxonomy:
    """Test suite for BloomsTaxonomy utility class."""

    def test_validate_verb_valid(self):
        """Test verb validation with valid verbs."""
        assert BloomsTaxonomy.validate_verb("define", "Remember")
        assert BloomsTaxonomy.validate_verb("explain", "Understand")
        assert BloomsTaxonomy.validate_verb("apply", "Apply")
        assert BloomsTaxonomy.validate_verb("analyze", "Analyze")
        assert BloomsTaxonomy.validate_verb("evaluate", "Evaluate")
        assert BloomsTaxonomy.validate_verb("create", "Create")

    def test_validate_verb_invalid(self):
        """Test verb validation with invalid verbs."""
        assert not BloomsTaxonomy.validate_verb("code", "Remember")
        assert not BloomsTaxonomy.validate_verb("write", "Apply")
        assert not BloomsTaxonomy.validate_verb("test", "Analyze")

    def test_validate_verb_case_insensitive(self):
        """Test that verb validation is case-insensitive."""
        assert BloomsTaxonomy.validate_verb("DEFINE", "Remember")
        assert BloomsTaxonomy.validate_verb("Define", "Remember")
        assert BloomsTaxonomy.validate_verb("define", "Remember")
        assert BloomsTaxonomy.validate_verb("  define  ", "Remember")  # With whitespace

    def test_validate_verb_invalid_level(self):
        """Test verb validation with invalid level."""
        assert not BloomsTaxonomy.validate_verb("test", "InvalidLevel")
        assert not BloomsTaxonomy.validate_verb("test", "")

    def test_get_random_verb(self):
        """Test getting random verb for each level."""
        for level in ["Remember", "Understand", "Apply", "Analyze", "Evaluate", "Create"]:
            verb = BloomsTaxonomy.get_random_verb(level)
            assert isinstance(verb, str)
            assert len(verb) > 0
            # Verify it's actually from the approved list
            assert BloomsTaxonomy.validate_verb(verb, level)

    def test_get_random_verb_invalid_level(self):
        """Test getting random verb for invalid level."""
        verb = BloomsTaxonomy.get_random_verb("InvalidLevel")
        assert verb == "demonstrate"  # Default fallback

    def test_get_all_verbs(self):
        """Test getting all verbs."""
        all_verbs = BloomsTaxonomy.get_all_verbs()
        assert isinstance(all_verbs, dict)
        assert len(all_verbs) == 6  # 6 levels
        for level in ["Remember", "Understand", "Apply", "Analyze", "Evaluate", "Create"]:
            assert level in all_verbs
            assert isinstance(all_verbs[level], list)
            assert len(all_verbs[level]) > 0

    def test_get_all_verbs_is_copy(self):
        """Test that get_all_verbs returns a copy, not the original."""
        verbs1 = BloomsTaxonomy.get_all_verbs()
        verbs2 = BloomsTaxonomy.get_all_verbs()
        assert verbs1 is not verbs2  # Different instances
        assert verbs1 == verbs2  # Same content


# =============================================================================
# BloomLevel Enum Tests
# =============================================================================

class TestBloomLevel:
    """Test suite for BloomLevel enum."""

    def test_bloom_level_values(self):
        """Test that all expected Bloom's levels are present."""
        assert BloomLevel.REMEMBER.value == "Remember"
        assert BloomLevel.UNDERSTAND.value == "Understand"
        assert BloomLevel.APPLY.value == "Apply"
        assert BloomLevel.ANALYZE.value == "Analyze"
        assert BloomLevel.EVALUATE.value == "Evaluate"
        assert BloomLevel.CREATE.value == "Create"

    def test_bloom_level_iteration(self):
        """Test iterating over all Bloom's levels."""
        levels = list(BloomLevel)
        assert len(levels) == 6
        expected_levels = ["Remember", "Understand", "Apply", "Analyze", "Evaluate", "Create"]
        actual_levels = [level.value for level in levels]
        assert actual_levels == expected_levels

    def test_bloom_level_from_string(self):
        """Test creating BloomLevel from string."""
        level = BloomLevel("Understand")
        assert level == BloomLevel.UNDERSTAND

    def test_bloom_level_invalid_string(self):
        """Test that invalid string raises error."""
        with pytest.raises(ValueError):
            BloomLevel("InvalidLevel")


# =============================================================================
# Edge Cases and Boundary Conditions
# =============================================================================

class TestEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_learning_objective_very_long_content(self):
        """Test objective with very long content."""
        long_content = "test " * 1000  # 5000 characters
        objective = LearningObjective(
            id="LO-001",
            verb="explain",
            content=long_content,
            level=BloomLevel.UNDERSTAND,
        )
        assert len(objective.content) == len(long_content)

    def test_quiz_question_very_long_stem(self):
        """Test quiz question with very long stem."""
        long_stem = "What is " + "test " * 500 + "?"
        question = QuizQuestion(
            stem=long_stem,
            correct_answer="Test answer",
            distractors=["Wrong 1", "Wrong 2", "Wrong 3"],
            explanation="Test explanation",
        )
        assert len(question.stem) == len(long_stem)

    def test_quiz_question_very_long_answers(self):
        """Test quiz question with very long answer options."""
        long_answer = "answer " * 500  # Long answer
        question = QuizQuestion(
            stem="What is test?",
            correct_answer=long_answer,
            distractors=[long_answer + " 1", long_answer + " 2", long_answer + " 3"],
            explanation="Test explanation",
        )
        assert len(question.correct_answer) == len(long_answer)

    def test_course_structure_with_maximum_objectives(self):
        """Test course structure with many objectives."""
        objectives = []
        for i in range(50):  # Create 50 objectives
            objectives.append(
                LearningObjective(
                    id=f"LO-{i:03d}",
                    verb="explain",
                    content=f"test content {i}",
                    level=BloomLevel.UNDERSTAND,
                )
            )
        structure = CourseStructure(
            topic="Test Topic",
            objectives=objectives,
        )
        assert len(structure.objectives) == 50

    def test_special_characters_in_content(self):
        """Test handling special characters in content."""
        special_content = "Test with émojis 🎉 and spëcial çharacters"
        objective = LearningObjective(
            id="LO-001",
            verb="explain",
            content=special_content,
            level=BloomLevel.UNDERSTAND,
        )
        assert objective.content == special_content

    def test_unicode_in_quiz_question(self):
        """Test handling unicode in quiz questions."""
        question = QuizQuestion(
            stem="What is 测试?",
            correct_answer="答案",
            distractors=["错误 1", "错误 2", "错误 3"],
            explanation="测试解释",
        )
        assert question.stem == "What is 测试?"

    def test_newlines_in_text_fields(self):
        """Test handling newlines in text fields."""
        objective = LearningObjective(
            id="LO-001",
            verb="explain",
            content="Line 1\nLine 2\nLine 3",
            level=BloomLevel.UNDERSTAND,
        )
        assert "\n" in objective.content
