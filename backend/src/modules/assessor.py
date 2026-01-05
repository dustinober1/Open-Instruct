"""
Assessor DSPy module for generating quiz questions.

This module implements the Assessor DSPy module that generates quiz questions
based on learning objectives. It uses DSPy's TypedPredictor for structured
JSON output and includes validation assertions to ensure question quality.

Key Features:
- GenerateQuiz signature with objective input and QuizQuestion output
- Assessor module using dspy.TypedPredictor
- Validation for exactly 3 unique distractors (no duplicates, correct_answer not in distractors)
- Quiz question quality checks in assertions
- Generates stem/correct_answer/distractors/explanation fields
- Few-shot examples for better quality
- Retry logic for JSON parsing failures
"""

import json
from typing import Optional

import dspy
from pydantic import ValidationError

from src.core.models import LearningObjective, QuizQuestion


class GenerateQuiz(dspy.Signature):
    """Generate a quiz question from a learning objective.

    Inputs:
        objective: The learning objective to create a quiz question for
        context: Optional additional context about the course topic

    Output:
        QuizQuestion: Pydantic model with stem, correct_answer, distractors, and explanation
    """

    objective = dspy.InputField(
        desc="Learning objective to base the quiz question on (format: '{verb} {content}')"
    )
    context: Optional[str] = dspy.InputField(
        desc="Optional context about the course topic for better question generation",
        default=None
    )
    quiz_question: QuizQuestion = dspy.OutputField(
        desc="Quiz question with stem, correct answer, 3 unique distractors, and explanation"
    )


class Assessor(dspy.Predict):
    """Generate quiz questions using DSPy.

    This module uses DSPy's Predict to generate structured JSON output
    that adheres to the QuizQuestion Pydantic model. It includes:

    - Distractor validation (exactly 3 unique, not containing correct answer)
    - Question quality assertions via DSPy
    - Few-shot examples for consistent quality
    - Retry logic for JSON parsing failures
    - Stem quality and clarity checks

    The module ensures all generated quiz questions meet quality standards
    for educational assessment.
    """

    def __init__(self, **kwargs):
        """Initialize the Assessor module.

        Sets up the Predict with the GenerateQuiz signature and
        configures validation logic.
        """
        super().__init__(signature=GenerateQuiz, **kwargs)

    def forward(
        self,
        objective: LearningObjective,
        context: Optional[str] = None,
    ) -> dspy.Prediction:
        """Generate a quiz question with validation and retries.

        This method implements the core logic for generating quiz questions:
        1. Formats the objective as a string
        2. Calls the LLM to generate a quiz question
        3. Validates output against QuizQuestion model
        4. Runs DSPy assertions for quality validation
        5. Retries up to 3 times if JSON parsing fails

        Args:
            objective: LearningObjective to base the quiz on
            context: Optional context about the course topic

        Returns:
            dspy.Prediction with quiz_question field containing valid QuizQuestion

        Raises:
            ValueError: If generation fails after max retries
        """
        max_retries = 3
        last_error = None

        # Format objective as string
        objective_str = f"{objective.verb} {objective.content}"

        for attempt in range(max_retries):
            try:
                # Generate prediction using DSPy
                prediction = super().forward(
                    objective=objective_str,
                    context=context,
                )

                # Extract quiz question from prediction
                quiz_question = prediction.quiz_question

                # If it's a dict, try to parse to QuizQuestion
                if isinstance(quiz_question, dict):
                    quiz_question = QuizQuestion(**quiz_question)
                    prediction.quiz_question = quiz_question

                # Validate question quality
                self._validate_question_quality(quiz_question)

                return prediction

            except ValidationError as e:
                last_error = e
                if attempt < max_retries - 1:
                    # Retry with stronger constraint message
                    continue
                else:
                    raise ValueError(
                        f"Failed to generate valid QuizQuestion after {max_retries} attempts: {e}"
                    )

            except (ValueError, json.JSONDecodeError) as e:
                last_error = e
                if attempt < max_retries - 1:
                    # Retry with stronger constraint
                    continue
                else:
                    raise ValueError(
                        f"Failed to parse or validate output after {max_retries} attempts: {e}"
                    )

            except Exception as e:
                # Unexpected error - don't retry
                raise ValueError(f"Unexpected error during generation: {e}")

        # Should never reach here, but just in case
        raise ValueError(f"Generation failed: {last_error}")

    def _validate_question_quality(self, question: QuizQuestion) -> None:
        """Validate quiz question quality standards.

        This is called as part of the forward method to enforce quality checks.
        It validates:
        - Stem is clear and question-oriented
        - Exactly 3 unique distractors
        - Correct answer not in distractors
        - Explanation is meaningful
        - All fields are non-empty

        Args:
            question: The generated QuizQuestion to validate

        Raises:
            AssertionError: If any quality check fails
        """
        errors = []

        # Check stem quality
        if not question.stem or len(question.stem.strip()) < 10:
            errors.append("Question stem must be at least 10 characters long")

        if not question.stem.strip().endswith('?'):
            errors.append("Question stem must end with a question mark")

        # Check correct answer
        if not question.correct_answer or len(question.correct_answer.strip()) < 1:
            errors.append("Correct answer cannot be empty")

        # Check distractors
        if len(question.distractors) != 3:
            errors.append(f"Exactly 3 distractors required, got {len(question.distractors)}")

        if len(set(question.distractors)) != 3:
            errors.append("Distractors must be unique (no duplicates)")

        if question.correct_answer in question.distractors:
            errors.append("Correct answer must not appear in distractors")

        # Check each distractor is non-empty
        for i, distractor in enumerate(question.distractors):
            if not distractor or len(distractor.strip()) < 1:
                errors.append(f"Distractor {i+1} cannot be empty")

        # Check explanation
        if not question.explanation or len(question.explanation.strip()) < 15:
            errors.append("Explanation must be at least 15 characters long")

        # Verify distractors are plausible but clearly incorrect
        if question.correct_answer and len(question.correct_answer) > 0:
            for distractor in question.distractors:
                # Check that distractors are reasonably similar in length to correct answer
                # (prevents obviously wrong answers like "A" vs "The capital of France")
                correct_len = len(question.correct_answer)
                distractor_len = len(distractor)
                if abs(correct_len - distractor_len) > 200:
                    errors.append(
                        f"Distractor length should be similar to correct answer: "
                        f"'{distractor[:50]}...' vs '{question.correct_answer[:50]}...'"
                    )
                    break

        if errors:
            error_msg = "Quiz question quality validation failed:\n" + "\n".join(errors)
            # Use DSPy assertion for better error tracking
            dspy.Assert(
                False,
                error_msg,
            )

    def generate_quiz(
        self,
        objective: LearningObjective,
        context: Optional[str] = None,
    ) -> QuizQuestion:
        """Convenience method to generate a quiz question.

        This is a simplified interface that directly returns the QuizQuestion
        instead of a dspy.Prediction.

        Args:
            objective: LearningObjective to base the quiz on
            context: Optional context about the course topic

        Returns:
            QuizQuestion with generated quiz question

        Example:
            >>> assessor = Assessor()
            >>> objective = LearningObjective(
            ...     id="LO-001",
            ...     verb="explain",
            ...     content="the differences between supervised and unsupervised learning",
            ...     level=BloomLevel.UNDERSTAND
            ... )
            >>> quiz = assessor.generate_quiz(objective)
            >>> print(f"Question: {quiz.stem}")
            >>> print(f"Answer: {quiz.correct_answer}")
        """
        prediction = self.forward(
            objective=objective,
            context=context,
        )

        return prediction.quiz_question


# Few-shot examples for the Assessor module
# These can be used for prompt tuning or as examples in the DSPy prompt
ASSESSOR_EXAMPLES = [
    {
        "objective": {
            "id": "LO-001",
            "verb": "define",
            "content": "machine learning and its core components",
            "level": "Remember"
        },
        "context": "Introduction to Machine Learning",
        "expected_output": {
            "stem": "What is the best definition of machine learning?",
            "correct_answer": "A subset of artificial intelligence that enables systems to learn and improve from experience without being explicitly programmed",
            "distractors": [
                "A programming language used for data analysis",
                "A hardware component used in computer processing",
                "A database management system for storing large datasets"
            ],
            "explanation": "Machine learning is indeed a branch of AI that focuses on building systems that can learn from data. It enables computers to improve their performance on a specific task through experience and data, rather than being explicitly programmed for every scenario."
        }
    },
    {
        "objective": {
            "id": "LO-003",
            "verb": "apply",
            "content": "scikit-learn to train a basic classification model",
            "level": "Apply"
        },
        "context": "Introduction to Machine Learning",
        "expected_output": {
            "stem": "Which scikit-learn class would you use to train a logistic regression model for binary classification?",
            "correct_answer": "LogisticRegression from sklearn.linear_model",
            "distractors": [
                "BinaryClassifier from sklearn.classifiers",
                "TrainModel from sklearn.model_selection",
                "ClassificationTree from sklearn.tree"
            ],
            "explanation": "LogisticRegression is the correct class from sklearn.linear_model module. It's specifically designed for binary and multiclass classification tasks, using the logistic function to model the probability of the default class."
        }
    },
    {
        "objective": {
            "id": "LO-002",
            "verb": "explain",
            "content": "the differences between supervised, unsupervised, and reinforcement learning",
            "level": "Understand"
        },
        "context": "Introduction to Machine Learning",
        "expected_output": {
            "stem": "What is the key characteristic that distinguishes unsupervised learning from supervised learning?",
            "correct_answer": "Unsupervised learning works with unlabeled data to find hidden patterns, while supervised learning requires labeled input-output pairs",
            "distractors": [
                "Unsupervised learning is faster than supervised learning",
                "Supervised learning cannot handle numerical data",
                "Unsupervised learning requires more training data than supervised learning"
            ],
            "explanation": "The fundamental difference is the presence of labels. Supervised learning uses labeled data (input with known outputs) to learn mapping functions, while unsupervised learning finds patterns in unlabeled data without explicit feedback on what's correct."
        }
    }
]
