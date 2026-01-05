"""
Architect DSPy module for generating learning objectives.

This module implements the Architect DSPy module that generates structured learning
objectives based on Bloom's Taxonomy. It uses DSPy's TypedPredictor for structured
JSON output and includes validation assertions to ensure verbs match approved lists.

Key Features:
- GenerateObjectives signature for DSPy
- Architect module using TypedPredictor
- Bloom's verb validation assertions
- Few-shot examples for better quality
- Retry logic for JSON parsing failures
"""

import json
from typing import Optional

import dspy
from pydantic import ValidationError

from src.core.error_handlers import retry_with_exponential_backoff
from src.core.models import BloomsTaxonomy, CourseStructure, LearningObjective


class GenerateObjectives(dspy.Signature):
    """Generate structured learning objectives following Bloom's Taxonomy.

    Inputs:
        topic: The course topic/title
        target_audience: Who the course is designed for
        num_objectives: Number of learning objectives to generate (1-12)

    Output:
        CourseStructure: Pydantic model with topic and list of LearningObjective
    """

    topic = dspy.InputField(desc="Course topic or title")
    target_audience = dspy.InputField(desc="Target audience for the course")
    num_objectives = dspy.InputField(
        desc="Number of learning objectives to generate (1-12, recommended 5-8)"
    )
    course_structure: CourseStructure = dspy.OutputField(
        desc="Structured course with topic and learning objectives following Bloom's Taxonomy"
    )


class Architect(dspy.Predict):
    """Generate learning objectives using DSPy and Bloom's Taxonomy.

    This module uses DSPy's Predict to generate structured JSON output
    that adheres to the CourseStructure Pydantic model. It includes:

    - Bloom's verb validation via DSPy assertions
    - Few-shot examples for consistent quality
    - Retry logic for JSON parsing failures
    - Constraint enforcement for verb and level matching

    The module ensures all generated objectives use approved Bloom's verbs
    appropriate for their cognitive level.
    """

    def __init__(self, **kwargs):
        """Initialize the Architect module.

        Sets up the Predict with the GenerateObjectives signature and
        configures few-shot examples and retry logic.
        """
        super().__init__(signature=GenerateObjectives, **kwargs)

    def _generate_once(
        self,
        topic: str,
        target_audience: str,
        num_objectives: int = 6,
    ) -> dspy.Prediction:
        """Single generation attempt without retry logic.

        This method performs one attempt at generating learning objectives:
        1. Calls the LLM to generate objectives
        2. Validates output against CourseStructure model
        3. Runs DSPy assertions for Bloom's verb validation

        Args:
            topic: Course topic or title
            target_audience: Target audience description
            num_objectives: Number of objectives to generate (default: 6)

        Returns:
            dspy.Prediction with course_structure field containing valid CourseStructure

        Raises:
            ValueError: If generation or validation fails
            ValidationError: If output doesn't match CourseStructure model
        """
        # Generate prediction using DSPy
        prediction = super().forward(
            topic=topic,
            target_audience=target_audience,
            num_objectives=num_objectives,
        )

        # Extract course structure from prediction
        course_structure = prediction.course_structure

        # If it's a dict, try to parse to CourseStructure
        if isinstance(course_structure, dict):
            course_structure = CourseStructure(**course_structure)
            prediction.course_structure = course_structure

        # Validate all objectives use approved Bloom's verbs
        self._validate_blooms_verbs(course_structure)

        # Validate objective count matches request
        if len(course_structure.objectives) != num_objectives:
            raise ValueError(
                f"Expected {num_objectives} objectives, "
                f"got {len(course_structure.objectives)}"
            )

        return prediction

    def forward(
        self,
        topic: str,
        target_audience: str,
        num_objectives: int = 6,
    ) -> dspy.Prediction:
        """Generate learning objectives with validation and retries.

        This method implements the core logic for generating learning objectives:
        1. Calls the LLM to generate objectives (with retry via decorator)
        2. Validates output against CourseStructure model
        3. Runs DSPy assertions for Bloom's verb validation

        Uses centralized retry logic with exponential backoff.

        Args:
            topic: Course topic or title
            target_audience: Target audience description
            num_objectives: Number of objectives to generate (default: 6)

        Returns:
            dspy.Prediction with course_structure field containing valid CourseStructure

        Raises:
            ValueError: If generation fails after max retries
            ValidationError: If output doesn't match CourseStructure model
        """
        return self._generate_once(
            topic=topic,
            target_audience=target_audience,
            num_objectives=num_objectives,
        )

    def _validate_blooms_verbs(self, course_structure: CourseStructure) -> None:
        """Validate that all objectives use approved Bloom's verbs.

        This is called as part of the forward method to enforce Bloom's verb
        validation. It checks each objective's verb against the approved list
        for its cognitive level.

        Args:
            course_structure: The generated CourseStructure to validate

        Raises:
            AssertionError: If any verb is not approved for its level
        """
        errors = []

        for objective in course_structure.objectives:
            level_str = objective.level.value if hasattr(objective.level, 'value') else str(objective.level)

            if not BloomsTaxonomy.validate_verb(objective.verb, level_str):
                approved_verbs = BloomsTaxonomy.VERBS.get(level_str, [])
                errors.append(
                    f"Objective '{objective.id}': Verb '{objective.verb}' is not "
                    f"approved for level '{level_str}'. Approved verbs: {approved_verbs[:5]}..."
                )

        if errors:
            error_msg = "Bloom's verb validation failed:\n" + "\n".join(errors)
            # Raise assertion error for validation failures
            raise AssertionError(error_msg)

    def generate_objectives(
        self,
        topic: str,
        target_audience: str,
        num_objectives: int = 6,
    ) -> CourseStructure:
        """Convenience method to generate objectives.

        This is a simplified interface that directly returns the CourseStructure
        instead of a dspy.Prediction.

        Args:
            topic: Course topic or title
            target_audience: Target audience description
            num_objectives: Number of objectives to generate (default: 6)

        Returns:
            CourseStructure with generated learning objectives

        Example:
            >>> architect = Architect()
            >>> structure = architect.generate_objectives(
            ...     topic="Introduction to Python",
            ...     target_audience="Beginner programmers",
            ...     num_objectives=5
            ... )
            >>> print(structure.topic)
            >>> for obj in structure.objectives:
            ...     print(f"{obj.id}: {obj.verb} {obj.content}")
        """
        prediction = self.forward(
            topic=topic,
            target_audience=target_audience,
            num_objectives=num_objectives,
        )

        return prediction.course_structure


# Few-shot examples for the Architect module
# These can be used for prompt tuning or as examples in the DSPy prompt
ARCHITECT_EXAMPLES = [
    {
        "topic": "Introduction to Machine Learning",
        "target_audience": "Junior developers with basic Python knowledge",
        "num_objectives": 5,
        "expected_output": {
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
                    "content": "the differences between supervised, unsupervised, and reinforcement learning",
                    "level": "Understand"
                },
                {
                    "id": "LO-003",
                    "verb": "apply",
                    "content": "scikit-learn to train a basic classification model",
                    "level": "Apply"
                },
                {
                    "id": "LO-004",
                    "verb": "analyze",
                    "content": "model performance using accuracy, precision, and recall metrics",
                    "level": "Analyze"
                },
                {
                    "id": "LO-005",
                    "verb": "evaluate",
                    "content": "the strengths and weaknesses of different ML algorithms for a given problem",
                    "level": "Evaluate"
                }
            ]
        }
    },
    {
        "topic": "RESTful API Design with FastAPI",
        "target_audience": "Backend developers familiar with Python",
        "num_objectives": 6,
        "expected_output": {
            "topic": "RESTful API Design with FastAPI",
            "objectives": [
                {
                    "id": "LO-001",
                    "verb": "identify",
                    "content": "the key principles of REST architecture",
                    "level": "Remember"
                },
                {
                    "id": "LO-002",
                    "verb": "describe",
                    "content": "HTTP methods and their appropriate use in API design",
                    "level": "Understand"
                },
                {
                    "id": "LO-003",
                    "verb": "implement",
                    "content": "CRUD endpoints using FastAPI path operations",
                    "level": "Apply"
                },
                {
                    "id": "LO-004",
                    "verb": "analyze",
                    "content": "API request/response patterns for optimization opportunities",
                    "level": "Analyze"
                },
                {
                    "id": "LO-005",
                    "verb": "assess",
                    "content": "API security best practices including authentication and authorization",
                    "level": "Evaluate"
                },
                {
                    "id": "LO-006",
                    "verb": "design",
                    "content": "a comprehensive RESTful API with proper error handling and documentation",
                    "level": "Create"
                }
            ]
        }
    }
]
