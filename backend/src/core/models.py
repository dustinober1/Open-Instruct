"""
Bloom's Taxonomy data models and validation.

This module implements the complete Bloom's Taxonomy framework with:
- 6 cognitive levels (Remember, Understand, Apply, Analyze, Evaluate, Create)
- 180 approved verbs (30 per level)
- Pydantic models for learning objectives, course structure, and quiz questions
- Verb validation logic for LLM output enforcement
"""

from enum import Enum
from typing import Dict, List

from pydantic import BaseModel, Field, field_validator


class BloomLevel(str, Enum):
    """Bloom's Taxonomy cognitive levels."""

    REMEMBER = "Remember"
    UNDERSTAND = "Understand"
    APPLY = "Apply"
    ANALYZE = "Analyze"
    EVALUATE = "Evaluate"
    CREATE = "Create"


class LearningObjective(BaseModel):
    """A single learning objective following Bloom's Taxonomy."""

    id: str = Field(..., description="Unique identifier (e.g., LO-001)")
    verb: str = Field(..., description="Action verb from approved Bloom's list")
    content: str = Field(..., description="The learning objective content")
    level: BloomLevel = Field(..., description="Bloom's cognitive level")


class CourseStructure(BaseModel):
    """Structured course with topic and learning objectives."""

    topic: str = Field(..., description="Course topic title")
    objectives: List[LearningObjective] = Field(
        ...,
        description="List of learning objectives following Bloom's progression",
        min_length=1,
    )


class QuizQuestion(BaseModel):
    """A quiz question with stem, choices, and explanation."""

    stem: str = Field(..., description="Question stem/prompt")
    correct_answer: str = Field(..., description="Correct answer choice")
    distractors: List[str] = Field(
        ..., description="Exactly 3 unique incorrect answer choices", min_length=3, max_length=3
    )
    explanation: str = Field(..., description="Explanation of why answer is correct")

    @field_validator("distractors")
    @classmethod
    def validate_distractors(cls, v: List[str], info) -> List[str]:
        """Ensure exactly 3 unique distractors that differ from correct answer."""
        if len(v) != 3:
            raise ValueError("Exactly 3 distractors required")

        if len(set(v)) != 3:
            raise ValueError("Distractors must be unique")

        # Check against correct_answer if it exists in validation context
        if "correct_answer" in info.data:
            correct = info.data["correct_answer"]
            if correct in v:
                raise ValueError("Distractors must not contain correct_answer")

        return v


class BloomsTaxonomy:
    """
    Encapsulate Bloom's Taxonomy verb lists and validation logic.

    Provides:
    - Complete verb database (180 verbs across 6 levels)
    - Verb validation against approved lists
    - Random verb selection for testing/fallback
    """

    # Complete verb lists (DO NOT MODIFY WITHOUT TEAM APPROVAL)
    VERBS: Dict[str, List[str]] = {
        "Remember": [
            "define",
            "list",
            "name",
            "identify",
            "recall",
            "recognize",
            "label",
            "match",
            "memorize",
            "repeat",
            "state",
            "select",
            "locate",
            "tell",
            "quote",
            "enumerate",
            "outline",
            "describe",
            "who",
            "what",
            "when",
            "where",
            "which",
            "how",
            "show",
            "mark",
            "spell",
            "find",
            "cite",
            "tabulate",
        ],
        "Understand": [
            "explain",
            "describe",
            "summarize",
            "interpret",
            "paraphrase",
            "clarify",
            "discuss",
            "illustrate",
            "demonstrate",
            "exemplify",
            "rephrase",
            "translate",
            "convert",
            "estimate",
            "infer",
            "predict",
            "conclude",
            "differentiate",
            "distinguish",
            "compare",
            "contrast",
            "extend",
            "generalize",
            "give examples",
            "restate",
            "express",
            "indicate",
            "reason",
            "derive",
            "grasp",
        ],
        "Apply": [
            "apply",
            "use",
            "implement",
            "execute",
            "employ",
            "utilize",
            "practice",
            "perform",
            "operate",
            "manipulate",
            "modify",
            "change",
            "solve",
            "calculate",
            "compute",
            "determine",
            "discover",
            "verify",
            "validate",
            "check",
            "test",
            "debug",
            "trace",
            "run",
            "build",
            "construct",
            "create",
            "generate",
            "produce",
            "develop",
        ],
        "Analyze": [
            "analyze",
            "differentiate",
            "distinguish",
            "examine",
            "investigate",
            "inspect",
            "explore",
            "compare",
            "contrast",
            "categorize",
            "classify",
            "break down",
            "deconstruct",
            "separate",
            "discriminate",
            "detect",
            "identify patterns",
            "recognize structure",
            "find",
            "diagnose",
            "troubleshoot",
            "audit",
            "review",
            "assess",
            "evaluate",
            "organize",
            "outline",
            "structure",
            "map",
            "profile",
        ],
        "Evaluate": [
            "evaluate",
            "assess",
            "judge",
            "appraise",
            "estimate",
            "measure",
            "rate",
            "score",
            "value",
            "critique",
            "criticize",
            "recommend",
            "advise",
            "select",
            "choose",
            "prefer",
            "defend",
            "justify",
            "validate",
            "verify",
            "confirm",
            "corroborate",
            "support",
            "argue",
            "debate",
            "dispute",
            "question",
            "challenge",
            "weigh",
            "prioritize",
        ],
        "Create": [
            "create",
            "design",
            "construct",
            "build",
            "develop",
            "formulate",
            "generate",
            "produce",
            "manufacture",
            "compose",
            "assemble",
            "combine",
            "integrate",
            "merge",
            "blend",
            "synthesize",
            "originate",
            "devise",
            "invent",
            "concoct",
            "plan",
            "propose",
            "draft",
            "outline",
            "structure",
            "organize",
            "arrange",
            "author",
            "fabricate",
            "derive",
        ],
    }

    @classmethod
    def validate_verb(cls, verb: str, level: str) -> bool:
        """
        Check if verb is valid for given Bloom's level.

        Args:
            verb: The action verb to check
            level: The Bloom's level (e.g., "Remember")

        Returns:
            True if verb is approved for this level, False otherwise
        """
        approved_verbs = cls.VERBS.get(level, [])
        normalized_verb = verb.strip().lower()
        return normalized_verb in [v.lower() for v in approved_verbs]

    @classmethod
    def get_random_verb(cls, level: str) -> str:
        """
        Get a random verb from the specified level.

        Useful for testing or fallback generation when LLM produces invalid verb.

        Args:
            level: The Bloom's level to get verb from

        Returns:
            A random verb from the approved list, or "demonstrate" if level not found
        """
        import random

        verbs = cls.VERBS.get(level, [])
        return random.choice(verbs) if verbs else "demonstrate"

    @classmethod
    def get_all_verbs(cls) -> Dict[str, List[str]]:
        """
        Return complete verb list for all levels.

        Returns:
            Dictionary mapping level names to their approved verb lists
        """
        return cls.VERBS.copy()
