"""
Test the Assessor DSPy module.

This is a basic integration test to verify the Assessor module can generate
quiz questions from learning objectives.
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

import dspy
from src.core.models import BloomLevel, LearningObjective
from src.modules.assessor import Assessor
from src.core.dspy_client import configure_dspy


def test_assessor_basic():
    """Test basic quiz generation with a learning objective."""
    print("=" * 80)
    print("Testing Assessor Module - Basic Quiz Generation")
    print("=" * 80)

    # Configure DSPy (assuming Ollama for local testing)
    configure_dspy(base_url="http://localhost:11434", model="llama2")

    # Create a test learning objective
    objective = LearningObjective(
        id="LO-001",
        verb="explain",
        content="the differences between supervised and unsupervised learning",
        level=BloomLevel.UNDERSTAND
    )

    print(f"\nInput Learning Objective:")
    print(f"  ID: {objective.id}")
    print(f"  Verb: {objective.verb}")
    print(f"  Content: {objective.content}")
    print(f"  Level: {objective.level}")

    # Initialize Assessor
    print("\nInitializing Assessor module...")
    assessor = Assessor()

    # Generate quiz question
    print("Generating quiz question...")
    try:
        quiz = assessor.generate_quiz(
            objective=objective,
            context="Introduction to Machine Learning"
        )

        print("\n" + "=" * 80)
        print("SUCCESS - Generated Quiz Question:")
        print("=" * 80)
        print(f"\nQuestion Stem:\n  {quiz.stem}")
        print(f"\nCorrect Answer:\n  {quiz.correct_answer}")
        print(f"\nDistractors:")
        for i, distractor in enumerate(quiz.distractors, 1):
            print(f"  {i}. {distractor}")
        print(f"\nExplanation:\n  {quiz.explanation}")

        # Validate structure
        print("\n" + "=" * 80)
        print("Validation Checks:")
        print("=" * 80)
        print(f"✓ Stem ends with '?': {quiz.stem.endswith('?')}")
        print(f"✓ Stem length >= 10 chars: {len(quiz.stem) >= 10}")
        print(f"✓ Correct answer non-empty: {len(quiz.correct_answer) > 0}")
        print(f"✓ Exactly 3 distractors: {len(quiz.distractors) == 3}")
        print(f"✓ Distractors are unique: {len(set(quiz.distractors)) == 3}")
        print(f"✓ Correct not in distractors: {quiz.correct_answer not in quiz.distractors}")
        print(f"✓ Explanation length >= 15 chars: {len(quiz.explanation) >= 15}")

        print("\n" + "=" * 80)
        print("✓ TEST PASSED - Assessor module working correctly!")
        print("=" * 80)

        return True

    except Exception as e:
        print("\n" + "=" * 80)
        print(f"✗ TEST FAILED - Error: {e}")
        print("=" * 80)
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_assessor_basic()
    sys.exit(0 if success else 1)
